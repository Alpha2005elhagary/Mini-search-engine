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
    const { query } = await req.json()
    
    // Initialize Supabase Client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // 1. Perform Search using the RPC function
    const { data: results, error: searchError } = await supabaseClient.rpc(
      'search_documents',
      { query_text: query }
    )

    if (searchError) throw searchError

    // 2. Log to history
    await supabaseClient.from('search_history').insert({ query })

    // 3. (Optional) Simple Suggestion Logic
    // If no results, find the closest document name
    let suggestion = null
    if (!results || results.length === 0) {
       const { data: similar } = await supabaseClient
        .from('documents')
        .select('filename')
        .limit(1)
       if (similar && similar.length > 0) suggestion = similar[0].filename
    }

    return new Response(
      JSON.stringify({ results, suggestion }),
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
