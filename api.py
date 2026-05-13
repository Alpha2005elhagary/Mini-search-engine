from flask import Flask, request, jsonify
from flask_cors import CORS
from indexer import Indexer
from search import SearchEngine
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# Supabase Configuration
SUPABASE_URL = "https://oaysvjmzckqmnvyeoher.supabase.co"
SUPABASE_KEY = "sb_publishable_E1J5C2JG_YmAiKJuFZOd1Q_hIrt9k6q" # Use Service Role Key for backend if possible
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

indexer = Indexer()
search_engine = None

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'online',
        'message': 'Connected Python Backend is running!',
        'integration': 'Supabase + Python Logic'
    }), 200

@app.route('/process-supabase', methods=['POST'])
def process_supabase_file():
    """
    Downloads a file from Supabase Storage, extracts text using Python logic,
    and updates the Supabase PostgreSQL database.
    """
    data = request.json
    filename = data.get('filename')
    storage_path = data.get('storage_path') # e.g. 'documents/myfile.pdf'
    user_id = data.get('user_id')

    if not filename or not storage_path:
        return jsonify({'success': False, 'message': 'Missing filename or storage_path'}), 400

    try:
        # 1. Download file from Supabase Storage
        res = supabase.storage.from_('search-files').download(storage_path)
        local_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        
        with open(local_path, 'wb+') as f:
            f.write(res)

        # 2. Use Python Indexer logic to extract text
        ext = os.path.splitext(filename)[1].lower()
        content = indexer.index_file_to_text(local_path, ext)
        
        # Capture modification time
        mtime = datetime.fromtimestamp(os.path.getmtime(local_path)).isoformat()
        
        if not content:
            return jsonify({'success': False, 'message': 'Failed to extract text from file'}), 500

        # 3. Update Supabase PostgreSQL documents table
        supabase.table('documents').upsert({
            'filename': filename,
            'file_path': storage_path,
            'content': content,
            'file_type': ext.replace('.', '').upper(),
            'user_id': user_id,
            'modified_at': mtime
        }, on_conflict='file_path').execute()

        # Clean up local file
        os.remove(local_path)

        return jsonify({
            'success': True,
            'message': f'✅ Python logic processed {filename} and updated Supabase!'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """
    Optional: You can either search via Python or via Supabase SQL.
    This endpoint keeps your 'Did You Mean' logic from Python.
    """
    data = request.json
    query = data.get('query', '')
    user_id = data.get('user_id')
    
    # 1. Get results from Supabase PostgreSQL (Full Text Search)
    res = supabase.rpc('search_documents', {
        'query_text': query,
        'p_user_id': user_id
    }).execute()
    results = res.data

    # 2. Use Python logic for 'Did You Mean' suggestions
    suggestion = None
    if not results:
        # If no results, use Python search logic to find a suggestion
        if not search_engine:
            indexer.load_index() # Load local index if available for spellcheck
            search_engine = SearchEngine(indexer)
        suggestion = search_engine.did_you_mean(query)

    return jsonify({
        'results': results,
        'suggestion': suggestion
    })

@app.route('/stats', methods=['GET'])
def stats():
    """Fetches real-time stats from Supabase via Python"""
    user_id = request.args.get('user_id')
    query = supabase.table('documents').select('file_type')
    if user_id:
        query = query.eq('user_id', user_id)
    res = query.execute()
    data = res.data
    
    type_counts = {}
    for row in data:
        t = row['file_type']
        type_counts[t] = type_counts.get(t, 0) + 1
        
    return jsonify({
        'total_docs': len(data),
        'type_breakdown': type_counts
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
