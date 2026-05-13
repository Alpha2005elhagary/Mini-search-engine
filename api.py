from flask import Flask, request, jsonify
from flask_cors import CORS
from indexer import Indexer
from search import SearchEngine
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
# Enable CORS for all routes to allow Flutter Web/Emulator connections
CORS(app)

# Set the base directory to the location of api.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

indexer = Indexer()
search_engine = None

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'online',
        'message': 'Mini Search Engine API is running!',
        'endpoints': ['/upload', '/index-url', '/build', '/search', '/stats']
    }), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'success': True, 'message': f'File {filename} uploaded successfully! Re-build the index to include it.'}), 200

@app.route('/index-url', methods=['POST'])
def index_from_url():
    """Download a file from a public URL (e.g., Supabase Storage) and save it to the data folder."""
    import urllib.request
    data = request.json
    file_url = data.get('url')
    filename = data.get('filename')

    if not file_url or not filename:
        return jsonify({'success': False, 'message': 'Missing url or filename'}), 400

    try:
        safe_name = secure_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDER, safe_name)
        urllib.request.urlretrieve(file_url, file_path)
        return jsonify({
            'success': True,
            'message': f'✅ {safe_name} saved to server! Now tap "Start Indexing" to make it searchable.'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to download file: {str(e)}'}), 500

@app.route('/build', methods=['POST'])
def build_index():
    global search_engine, indexer
    data = request.json
    
    indexer.selected_formats = data.get('formats', [])
    folder = data.get('folder', 'data')
    
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except Exception as e:
            pass

    success = indexer.build_index(folder)
    
    if success:
        search_engine = SearchEngine(indexer)
        return jsonify({
            'success': True,
            'message': f'Indexed {indexer.doc_counter} files successfully!'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to build index. Check folder path and ensure there are valid documents inside.'
        })

@app.route('/search', methods=['POST'])
def search():
    global search_engine
    data = request.json
    
    if not search_engine:
        if indexer.load_index():
            search_engine = SearchEngine(indexer)
        else:
            return jsonify({'results': [], 'suggestion': None})
    
    query = data.get('query', '')
    
    date_from_str = data.get('date_from')
    date_to_str = data.get('date_to')
    file_type_str = data.get('file_type')
    
    date_from = datetime.strptime(date_from_str, '%Y-%m-%d') if date_from_str else None
    date_to = datetime.strptime(date_to_str, '%Y-%m-%d') if date_to_str else None
    file_type = [file_type_str] if file_type_str else None
    
    results = search_engine.search(query, date_from, date_to, file_type)
    
    formatted_results = []
    for doc_id, score in results[:50]:
        doc = search_engine.indexer.documents[doc_id]
        query_terms = query.lower().split()
        snippet = search_engine.get_snippet(doc_id, query_terms, 200)
        
        formatted_results.append({
            'filename': doc['filename'],
            'type': doc['type'],
            'score': score,
            'date': doc['date'],
            'snippet': snippet
        })
    
    suggestion = None
    if not results:
        suggestion = search_engine.did_you_mean(query)
    
    return jsonify({
        'results': formatted_results,
        'suggestion': suggestion
    })

@app.route('/stats', methods=['GET'])
def stats():
    global indexer
    if indexer.doc_counter == 0:
        if not indexer.load_index():
            return jsonify({'total_docs': 0, 'type_breakdown': {}, 'top_terms': []})
    
    type_counts = {}
    for doc in indexer.documents.values():
        t = doc['type']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    terms = sorted(indexer.inverted_index.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    
    return jsonify({
        'total_docs': indexer.doc_counter,
        'unique_terms': len(indexer.inverted_index),
        'type_breakdown': type_counts,
        'top_terms': [(word, len(docs)) for word, docs in terms]
    })

if __name__ == '__main__':
    if indexer.load_index():
        search_engine = SearchEngine(indexer)
        print("✅ Loaded existing index!")
    print("\n🚀 Starting Flutter API server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
