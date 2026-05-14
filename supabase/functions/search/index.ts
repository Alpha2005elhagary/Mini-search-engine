import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders });

  try {
    const { query: rawQuery, fileType, fromDate, toDate, page = 1, limit = 5 } = await req.json();
    const offset = (page - 1) * limit;

    const supabase = createClient(Deno.env.get('SUPABASE_URL') ?? '', Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '');
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) throw new Error('Unauthorized');
    const { data: { user } } = await supabase.auth.getUser(authHeader.replace('Bearer ', ''));
    if (!user) throw new Error('Invalid User');

    const fuzzyTerms: string[] = [];
    const phrases: string[] = [];
    
    // 1. Phrase Extraction
    let q = rawQuery.replace(/"([^"]+)"/g, (_, p) => {
      const parts = p.trim().split(/\s+/).filter((w: string) => w.length > 0);
      if (parts.length > 0) {
        phrases.push(`'${parts.join("' <-> '")}'`);
        return ` __PHRASE_${phrases.length - 1}__ `;
      }
      return '';
    });

    // 2. Tokenization with support for fuzzy~
    const tokens = q.match(/[()]|\bAND\b|\bOR\b|\bNOT\b|[^\s()~]+~[0-9]*|[^\s()]+/gi) || [];
    const intermediate: string[] = [];
    
    for (const t of tokens) {
      const u = t.toUpperCase();
      if (u === 'AND' || u === 'OR' || u === 'NOT' || t === '(' || t === ')') {
        intermediate.push(u === 'NOT' ? 'NOT' : u);
      } else {
        let term = '';
        if (t.startsWith('__PHRASE_')) {
          const idx = parseInt(t.match(/\d+/)![0]);
          term = phrases[idx];
        } else if (t.includes('~')) {
          const clean = t.split('~')[0].replace(/[^\w\u0600-\u06FF]/g, '');
          fuzzyTerms.push(clean);
          term = `'${clean}':*`;
        } else {
          const clean = t.replace(/[^\w\u0600-\u06FF]/g, '');
          term = `'${clean}':*`;
        }
        if (term !== "''" && term !== "'':*") intermediate.push(term);
      }
    }

    // 3. Implied AND
    const withAnd: string[] = [];
    for (let i = 0; i < intermediate.length; i++) {
      withAnd.push(intermediate[i]);
      if (i < intermediate.length - 1) {
        const curr = intermediate[i], next = intermediate[i + 1];
        const isOp = (x: string) => !['AND', 'OR', 'NOT', '(', ')'].includes(x);
        if ((isOp(curr) || curr === ')') && (isOp(next) || next === '(' || next === 'NOT')) withAnd.push('AND');
      }
    }

    // 4. Shunting-Yard to Postfix
    const output: string[] = [];
    const stack: string[] = [];
    const prec: any = { 'NOT': 3, 'AND': 2, 'OR': 1 };
    for (const t of withAnd) {
      if (t === '(') stack.push(t);
      else if (t === ')') {
        while (stack.length && stack[stack.length - 1] !== '(') output.push(stack.pop()!);
        stack.pop();
      } else if (prec[t]) {
        while (stack.length && stack[stack.length - 1] !== '(' && prec[stack[stack.length - 1]] >= prec[t]) output.push(stack.pop()!);
        stack.push(t);
      } else output.push(t);
    }
    while (stack.length) output.push(stack.pop()!);

    // 5. Build final tsquery string
    const ev: string[] = [];
    for (const t of output) {
      if (t === 'AND') { const r = ev.pop(), l = ev.pop(); ev.push(`(${l} & ${r})`); }
      else if (t === 'OR') { const r = ev.pop(), l = ev.pop(); ev.push(`(${l} | ${r})`); }
      else if (t === 'NOT') { const o = ev.pop(); ev.push(`(!${o})`); }
      else ev.push(t);
    }
    const finalTsQuery = ev[0] || '';

    // 6. Execute RPC
    const { data: results, error } = await supabase.rpc('search_documents_v2', {
      query_text: finalTsQuery,
      fuzzy_terms: fuzzyTerms,
      p_user_id: user.id,
      p_file_type: fileType || null,
      p_from_date: fromDate || null,
      p_to_date: toDate || null,
      p_limit: limit,
      p_offset: offset
    });

    if (error) throw error;

    let suggestion = null;
    if (results.length === 0) {
      const clean = rawQuery.replace(/[^\w\u0600-\u06FF\s]/g, '').split(/\s+/)[0];
      if (clean) {
        const { data: sugData } = await supabase.rpc('suggest_correction', { p_query: clean, p_user_id: user.id });
        suggestion = sugData;
      }
    }

    return new Response(JSON.stringify({
      results: results.map((r: any) => ({
        filename: r.filename,
        snippet: r.snippet,
        fileType: r.file_type,
        modifiedAt: r.modified_at,
        score: r.rank
      })),
      totalCount: results.length > 0 ? results[0].total_count : 0,
      suggestion
    }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } });

  } catch (e) {
    console.error(e);
    return new Response(JSON.stringify({ error: e.message }), { headers: corsHeaders, status: 400 });
  }
});
