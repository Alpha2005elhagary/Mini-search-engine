import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { query: rawQuery, fileType, fromDate, toDate } = await req.json()
    
    // Initialize Supabase Client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Get the user from the authorization header
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: corsHeaders });
    }

    const { data: { user }, error: authError } = await supabaseClient.auth.getUser(authHeader.replace('Bearer ', ''));
    if (authError || !user) {
      return new Response(JSON.stringify({ error: 'Invalid token' }), { status: 401, headers: corsHeaders });
    }

    const userId = user.id;
    
    // 1. Advanced Query Parsing
    const transformToTsQuery = (query: string): string => {
      if (!query) return '';

      // 1. Handle phrases: "hello world" -> (hello <-> world)
      let q = query.replace(/"([^"]+)"/g, (_, phrase) => {
        const words = phrase.trim().split(/\s+/).filter((w: string) => w.length > 0);
        return words.length > 0 ? `(${words.join(' <-> ')})` : '';
      });

      // 2. Tokenize: Operators (AND, OR, NOT), Grouping (()), Fuzzy (word~), Wildcards (*), and Words
      const tokens = q.match(/[()]|\bAND\b|\bOR\b|\bNOT\b|[^\s()~]+~\d*|[^\s()]+/gi) || [];
      const intermediate: string[] = [];

      for (const token of tokens) {
        const upper = token.toUpperCase();
        if (upper === 'AND') intermediate.push('&');
        else if (upper === 'OR') intermediate.push('|');
        else if (upper === 'NOT') intermediate.push('!');
        else if (token === '(' || token === ')') intermediate.push(token);
        else {
          // It's a term (word, fuzzy, or wildcard)
          let processed = token;
          if (token.includes('~')) {
            processed = token.split('~')[0] + ':*';
          } else if (token.includes('*') || token.includes('?')) {
            processed = token.replace(/[*?]/g, '') + ':*';
          }
          intermediate.push(processed);
        }
      }

      // 3. Insert implied & (AND) between adjacent terms/groups
      const final: string[] = [];
      for (let i = 0; i < intermediate.length; i++) {
        const curr = intermediate[i];
        final.push(curr);
        
        if (i < intermediate.length - 1) {
          const next = intermediate[i + 1];
          const isTermOrGroupOpen = (t: string) => !['&', '|', '!', '(', ')'].includes(t) || t === '(';
          const isTermOrGroupClose = (t: string) => !['&', '|', '!', '(', ')'].includes(t) || t === ')';
          
          // Insert & if we have:
          // [Term or )] followed by [Term or ( or !]
          const currIsOperand = !['&', '|', '!', '('].includes(curr);
          const nextIsOperandStart = !['&', '|', ')'].includes(next);
          
          if (currIsOperand && nextIsOperandStart) {
            final.push('&');
          }
        }
      }
      return final.join('');
    };

    const parsedQuery = transformToTsQuery(rawQuery);

    const { data: results, error: searchError } = await supabaseClient.rpc(
      'search_documents',
      { 
        query_text: parsedQuery, 
        p_user_id: userId,
        p_file_type: fileType || null,
        p_from_date: fromDate || null,
        p_to_date: toDate || null
      }
    )

    if (searchError) throw searchError

    // 3. Log to history
    await supabaseClient.from('search_history').insert({ 
      query: rawQuery,
      user_id: userId 
    })

    // 4. Suggestion Logic (Only on zero results)
    let suggestion = null
    if (!results || results.length === 0) {
      // 4. Suggestions: Clean the query before asking for spelling corrections
      const cleanQuery = rawQuery.replace(/~\d*/g, '').replace(/[*?]/g, '').replace(/\b(AND|OR|NOT)\b/gi, '').trim();
      
      const { data: suggestionData } = await supabaseClient.rpc(
        'suggest_correction',
        { 
          p_query: cleanQuery,
          p_user_id: userId
        }
      );
      suggestion = suggestionData
    }

    return new Response(
      JSON.stringify({ 
        results: results.map((r: any) => ({
          filename: r.filename,
          snippet: r.snippet || '', // Use the generated snippet from Postgres
          fileType: r.file_type,
          modifiedAt: r.modified_at
        })), 
        suggestion 
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200 
      }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400 
      }
    )
  }
})
