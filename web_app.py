# # web_app.py - Web-based UI using Flask
# from flask import Flask, render_template_string, request, jsonify
# from indexer import Indexer
# from search import SearchEngine
# from datetime import datetime
# import os

# app = Flask(__name__)

# # Global search engine instance
# search_engine = None
# indexer = Indexer()

# # HTML Template with built-in UI
# HTML_TEMPLATE = '''
# <!DOCTYPE html>
# <html>
# <head>
#     <title>🔍 Mini Search Engine</title>
#     <style>
#         * { margin: 0; padding: 0; box-sizing: border-box; }
#         body {
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             min-height: 100vh;
#             padding: 20px;
#         }
#         .container {
#             max-width: 1200px;
#             margin: 0 auto;
#         }
#         .card {
#             background: white;
#             border-radius: 15px;
#             padding: 25px;
#             margin-bottom: 20px;
#             box-shadow: 0 10px 30px rgba(0,0,0,0.2);
#         }
#         h1 {
#             color: #667eea;
#             margin-bottom: 10px;
#         }
#         .search-box {
#             display: flex;
#             gap: 10px;
#             margin-bottom: 20px;
#         }
#         .search-box input {
#             flex: 1;
#             padding: 15px;
#             font-size: 16px;
#             border: 2px solid #ddd;
#             border-radius: 10px;
#             transition: 0.3s;
#         }
#         .search-box input:focus {
#             outline: none;
#             border-color: #667eea;
#         }
#         .search-box button {
#             padding: 15px 30px;
#             background: #667eea;
#             color: white;
#             border: none;
#             border-radius: 10px;
#             cursor: pointer;
#             font-size: 16px;
#         }
#         .search-box button:hover {
#             background: #5a67d8;
#         }
#         .filters {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
#             gap: 15px;
#             margin-bottom: 20px;
#             padding: 15px;
#             background: #f7f7f7;
#             border-radius: 10px;
#         }
#         .filter-group {
#             display: flex;
#             flex-direction: column;
#             gap: 5px;
#         }
#         .filter-group label {
#             font-weight: bold;
#             color: #555;
#             font-size: 14px;
#         }
#         .filter-group input, .filter-group select {
#             padding: 8px;
#             border: 1px solid #ddd;
#             border-radius: 5px;
#         }
#         .result-item {
#             padding: 15px;
#             border-bottom: 1px solid #eee;
#             transition: 0.3s;
#         }
#         .result-item:hover {
#             background: #f9f9f9;
#         }
#         .result-title {
#             font-size: 18px;
#             font-weight: bold;
#             color: #667eea;
#             margin-bottom: 5px;
#         }
#         .result-meta {
#             font-size: 12px;
#             color: #888;
#             margin-bottom: 10px;
#         }
#         .result-snippet {
#             color: #555;
#             line-height: 1.5;
#         }
#         .highlight {
#             background: yellow;
#             font-weight: bold;
#         }
#         .pagination {
#             display: flex;
#             justify-content: center;
#             gap: 10px;
#             margin-top: 20px;
#         }
#         .pagination button {
#             padding: 8px 15px;
#             background: #667eea;
#             color: white;
#             border: none;
#             border-radius: 5px;
#             cursor: pointer;
#         }
#         .pagination button:disabled {
#             background: #ccc;
#             cursor: not-allowed;
#         }
#         .stats-grid {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
#             gap: 15px;
#         }
#         .stat-card {
#             background: #f7f7f7;
#             padding: 15px;
#             border-radius: 10px;
#             text-align: center;
#         }
#         .stat-number {
#             font-size: 32px;
#             font-weight: bold;
#             color: #667eea;
#         }
#         .format-checkbox {
#             display: inline-block;
#             margin-right: 15px;
#             margin-bottom: 10px;
#         }
#         button {
#             background: #667eea;
#             color: white;
#             border: none;
#             padding: 10px 20px;
#             border-radius: 5px;
#             cursor: pointer;
#             margin: 5px;
#         }
#         button:hover {
#             background: #5a67d8;
#         }
#         .suggestion {
#             background: #fff3cd;
#             border-left: 4px solid #ffc107;
#             padding: 10px;
#             margin-bottom: 20px;
#             border-radius: 5px;
#         }
#         .nav-tabs {
#             display: flex;
#             gap: 10px;
#             margin-bottom: 20px;
#             border-bottom: 2px solid #ddd;
#         }
#         .tab {
#             padding: 10px 20px;
#             cursor: pointer;
#             border: none;
#             background: none;
#         }
#         .tab.active {
#             color: #667eea;
#             border-bottom: 2px solid #667eea;
#         }
#         .tab-content {
#             display: none;
#         }
#         .tab-content.active {
#             display: block;
#         }
#         .message {
#             padding: 10px;
#             border-radius: 5px;
#             margin-bottom: 15px;
#         }
#         .message.success {
#             background: #d4edda;
#             color: #155724;
#             border: 1px solid #c3e6cb;
#         }
#         .message.error {
#             background: #f8d7da;
#             color: #721c24;
#             border: 1px solid #f5c6cb;
#         }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="card">
#             <h1>🔍 Mini Search Engine</h1>
#             <p>Index and search your documents with boolean, phrase, fuzzy, and wildcard queries</p>
            
#             <div class="nav-tabs">
#                 <button class="tab active" onclick="showTab('search')">🔎 Search</button>
#                 <button class="tab" onclick="showTab('build')">📚 Build Index</button>
#                 <button class="tab" onclick="showTab('stats')">📊 Statistics</button>
#             </div>
            
#             <!-- Build Index Tab -->
#             <div id="build-tab" class="tab-content active">
#                 <h3>Build Document Index</h3>
#                 <div id="build-message"></div>
#                 <div class="filters">
#                     <div class="filter-group">
#                         <label>Select file formats to index:</label>
#                         <div>
#                             <label class="format-checkbox"><input type="checkbox" value=".txt" class="format-check"> TXT</label>
#                             <label class="format-checkbox"><input type="checkbox" value=".pdf" class="format-check"> PDF</label>
#                             <label class="format-checkbox"><input type="checkbox" value=".json" class="format-check"> JSON</label>
#                             <label class="format-checkbox"><input type="checkbox" value=".csv" class="format-check"> CSV</label>
#                             <label class="format-checkbox"><input type="checkbox" value=".xlsx" class="format-check"> Excel</label>
#                         </div>
#                     </div>
#                     <div class="filter-group">
#                         <label>Folder path:</label>
#                         <input type="text" id="folder-path" placeholder="data" value="data">
#                     </div>
#                 </div>
#                 <button onclick="buildIndex()">🚀 Build / Refresh Index</button>
#             </div>
            
#             <!-- Search Tab -->
#             <div id="search-tab" class="tab-content">
#                 <div class="search-box">
#                     <input type="text" id="query" placeholder='Try: "information retrieval" OR cat~ OR comp*' >
#                     <button onclick="search()">🔍 Search</button>
#                 </div>
                
#                 <div class="filters">
#                     <div class="filter-group">
#                         <label>Date from:</label>
#                         <input type="date" id="date-from">
#                     </div>
#                     <div class="filter-group">
#                         <label>Date to:</label>
#                         <input type="date" id="date-to">
#                     </div>
#                     <div class="filter-group">
#                         <label>File type:</label>
#                         <select id="file-type">
#                             <option value="">All types</option>
#                             <option value="TXT">TXT</option>
#                             <option value="PDF">PDF</option>
#                             <option value="JSON">JSON</option>
#                             <option value="CSV">CSV</option>
#                             <option value="XLSX">Excel</option>
#                         </select>
#                     </div>
#                 </div>
                
#                 <div id="suggestion" class="suggestion" style="display:none;"></div>
#                 <div id="results"></div>
#                 <div id="pagination" class="pagination"></div>
#             </div>
            
#             <!-- Stats Tab -->
#             <div id="stats-tab" class="tab-content">
#                 <div id="stats-content"></div>
#             </div>
#         </div>
#     </div>
    
#     <script>
#         let currentResults = [];
#         let currentPage = 0;
#         let resultsPerPage = 5;
        
#         function showTab(tabName) {
#             document.querySelectorAll('.tab-content').forEach(tab => {
#                 tab.classList.remove('active');
#             });
#             document.getElementById(tabName + '-tab').classList.add('active');
            
#             document.querySelectorAll('.tab').forEach(tab => {
#                 tab.classList.remove('active');
#             });
#             event.target.classList.add('active');
            
#             if (tabName === 'stats') {
#                 loadStats();
#             }
#         }
        
#         async function buildIndex() {
#             const formats = Array.from(document.querySelectorAll('.format-check:checked'))
#                 .map(cb => cb.value);
            
#             if (formats.length === 0) {
#                 showMessage('build-message', 'Please select at least one format', 'error');
#                 return;
#             }
            
#             const folder = document.getElementById('folder-path').value;
            
#             showMessage('build-message', 'Building index... please wait', 'success');
            
#             const response = await fetch('/build', {
#                 method: 'POST',
#                 headers: {'Content-Type': 'application/json'},
#                 body: JSON.stringify({formats: formats, folder: folder})
#             });
            
#             const data = await response.json();
#             if (data.success) {
#                 showMessage('build-message', data.message, 'success');
#                 setTimeout(() => loadStats(), 1000);
#             } else {
#                 showMessage('build-message', data.message, 'error');
#             }
#         }
        
#         async function search() {
#             const query = document.getElementById('query').value;
#             if (!query) {
#                 alert('Please enter a search query');
#                 return;
#             }
            
#             const dateFrom = document.getElementById('date-from').value;
#             const dateTo = document.getElementById('date-to').value;
#             const fileType = document.getElementById('file-type').value;
            
#             const response = await fetch('/search', {
#                 method: 'POST',
#                 headers: {'Content-Type': 'application/json'},
#                 body: JSON.stringify({
#                     query: query,
#                     date_from: dateFrom,
#                     date_to: dateTo,
#                     file_type: fileType
#                 })
#             });
            
#             const data = await response.json();
            
#             if (data.suggestion) {
#                 const suggestionDiv = document.getElementById('suggestion');
#                 suggestionDiv.style.display = 'block';
#                 suggestionDiv.innerHTML = `💡 Did you mean: <strong>${data.suggestion}</strong>? 
#                     <button onclick="document.getElementById('query').value='${data.suggestion}'; search()">Try this</button>`;
#             } else {
#                 document.getElementById('suggestion').style.display = 'none';
#             }
            
#             currentResults = data.results || [];
#             currentPage = 0;
#             displayResults();
#         }
        
#         function displayResults() {
#             const resultsDiv = document.getElementById('results');
#             const paginationDiv = document.getElementById('pagination');
            
#             if (currentResults.length === 0) {
#                 resultsDiv.innerHTML = '<p>❌ No results found</p>';
#                 paginationDiv.innerHTML = '';
#                 return;
#             }
            
#             const start = currentPage * resultsPerPage;
#             const end = start + resultsPerPage;
#             const pageResults = currentResults.slice(start, end);
#             const totalPages = Math.ceil(currentResults.length / resultsPerPage);
            
#             resultsDiv.innerHTML = pageResults.map(result => `
#                 <div class="result-item">
#                     <div class="result-title">📄 ${result.filename}</div>
#                     <div class="result-meta">
#                         Type: ${result.type} | Score: ${result.score} | 
#                         Modified: ${result.date}
#                     </div>
#                     <div class="result-snippet">${result.snippet || 'No preview available'}</div>
#                 </div>
#             `).join('');
            
#             paginationDiv.innerHTML = `
#                 <button onclick="changePage(-1)" ${currentPage === 0 ? 'disabled' : ''}>◀ Previous</button>
#                 <span>Page ${currentPage + 1} of ${totalPages}</span>
#                 <button onclick="changePage(1)" ${currentPage === totalPages - 1 ? 'disabled' : ''}>Next ▶</button>
#             `;
#         }
        
#         function changePage(delta) {
#             currentPage += delta;
#             displayResults();
#         }
        
#         async function loadStats() {
#             const response = await fetch('/stats');
#             const stats = await response.json();
            
#             const statsDiv = document.getElementById('stats-content');
#             statsDiv.innerHTML = `
#                 <div class="stats-grid">
#                     <div class="stat-card">
#                         <div class="stat-number">${stats.total_docs}</div>
#                         <div>Total Documents</div>
#                     </div>
#                     <div class="stat-card">
#                         <div class="stat-number">${stats.unique_terms}</div>
#                         <div>Unique Terms</div>
#                     </div>
#                 </div>
#                 <h3>📁 Documents by Type</h3>
#                 <div class="stats-grid">
#                     ${Object.entries(stats.type_breakdown || {}).map(([type, count]) => `
#                         <div class="stat-card">
#                             <div class="stat-number">${count}</div>
#                             <div>${type}</div>
#                         </div>
#                     `).join('')}
#                 </div>
#                 <h3>🔥 Top 10 Most Frequent Terms</h3>
#                 <div class="stats-grid">
#                     ${(stats.top_terms || []).map(term => `
#                         <div class="stat-card">
#                             <div class="stat-number">${term[1]}</div>
#                             <div>"${term[0]}"</div>
#                         </div>
#                     `).join('')}
#                 </div>
#             `;
#         }
        
#         function showMessage(elementId, message, type) {
#             const div = document.getElementById(elementId);
#             div.innerHTML = `<div class="message ${type}">${message}</div>`;
#             setTimeout(() => {
#                 div.innerHTML = '';
#             }, 3000);
#         }
#     </script>
# </body>
# </html>
# '''

# @app.route('/')
# def index():
#     return render_template_string(HTML_TEMPLATE)

# @app.route('/build', methods=['POST'])
# def build_index():
#     global search_engine, indexer
#     data = request.json
    
#     indexer.selected_formats = data['formats']
#     folder = data.get('folder', 'data')
    
#     success = indexer.build_index(folder)
    
#     if success:
#         search_engine = SearchEngine(indexer)
#         return jsonify({
#             'success': True,
#             'message': f'Indexed {indexer.doc_counter} files successfully!'
#         })
#     else:
#         return jsonify({
#             'success': False,
#             'message': 'Failed to build index. Check folder path.'
#         })

# @app.route('/search', methods=['POST'])
# def search():
#     global search_engine
#     data = request.json
    
#     if not search_engine:
#         return jsonify({'results': [], 'suggestion': None})
    
#     # Parse date filters
#     date_from = datetime.strptime(data['date_from'], '%Y-%m-%d') if data.get('date_from') else None
#     date_to = datetime.strptime(data['date_to'], '%Y-%m-%d') if data.get('date_to') else None
#     file_type = [data['file_type']] if data.get('file_type') else None
    
#     results = search_engine.search(data['query'], date_from, date_to, file_type)
    
#     # Format results for display
#     formatted_results = []
#     for doc_id, score in results[:50]:  # Limit to 50 results
#         doc = search_engine.indexer.documents[doc_id]
        
#         # Get highlighted snippet
#         query_terms = data['query'].lower().split()
#         snippet = search_engine.get_snippet(doc_id, query_terms, 200)
        
#         formatted_results.append({
#             'filename': doc['filename'],
#             'type': doc['type'],
#             'score': score,
#             'date': doc['date'],
#             'snippet': snippet
#         })
    
#     # Get suggestion if no results
#     suggestion = None
#     if not results:
#         suggestion = search_engine.did_you_mean(data['query'])
    
#     return jsonify({
#         'results': formatted_results,
#         'suggestion': suggestion
#     })

# @app.route('/stats')
# def stats():
#     global indexer
#     if indexer.doc_counter == 0:
#         return jsonify({'total_docs': 0, 'type_breakdown': {}, 'top_terms': []})
    
#     # Type breakdown
#     type_counts = {}
#     for doc in indexer.documents.values():
#         t = doc['type']
#         type_counts[t] = type_counts.get(t, 0) + 1
    
#     # Top terms
#     terms = sorted(indexer.inverted_index.items(), 
#                    key=lambda x: len(x[1]), reverse=True)[:10]
    
#     return jsonify({
#         'total_docs': indexer.doc_counter,
#         'unique_terms': len(indexer.inverted_index),
#         'type_breakdown': type_counts,
#         'top_terms': [(word, len(docs)) for word, docs in terms]
#     })

# if __name__ == '__main__':
#     # Load existing index if available
#     if indexer.load_index():
#         search_engine = SearchEngine(indexer)
#         print("✅ Loaded existing index!")
    
#     print("\n🚀 Starting web server...")
#     print("🌐 Open your browser and go to: http://localhost:5000")
#     app.run(debug=True)




















# # web_app.py - Web-based UI with WORKING PAGINATION
# from flask import Flask, render_template_string, request, jsonify
# from indexer import Indexer
# from search import SearchEngine
# from datetime import datetime
# import os

# app = Flask(__name__)

# # Global search engine instance
# search_engine = None
# indexer = Indexer()

# # HTML Template with built-in UI
# HTML_TEMPLATE = '''
# <!DOCTYPE html>
# <html>
# <head>
#     <title>🔍 Mini Search Engine</title>
#     <style>
#         * { margin: 0; padding: 0; box-sizing: border-box; }
#         body {
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             min-height: 100vh;
#             padding: 20px;
#         }
#         .container {
#             max-width: 1200px;
#             margin: 0 auto;
#         }
#         .card {
#             background: white;
#             border-radius: 15px;
#             padding: 25px;
#             margin-bottom: 20px;
#             box-shadow: 0 10px 30px rgba(0,0,0,0.2);
#         }
#         h1 {
#             color: #667eea;
#             margin-bottom: 10px;
#         }
#         .search-box {
#             display: flex;
#             gap: 10px;
#             margin-bottom: 20px;
#         }
#         .search-box input {
#             flex: 1;
#             padding: 15px;
#             font-size: 16px;
#             border: 2px solid #ddd;
#             border-radius: 10px;
#             transition: 0.3s;
#         }
#         .search-box input:focus {
#             outline: none;
#             border-color: #667eea;
#         }
#         .search-box button {
#             padding: 15px 30px;
#             background: #667eea;
#             color: white;
#             border: none;
#             border-radius: 10px;
#             cursor: pointer;
#             font-size: 16px;
#         }
#         .search-box button:hover {
#             background: #5a67d8;
#         }
#         .filters {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
#             gap: 15px;
#             margin-bottom: 20px;
#             padding: 15px;
#             background: #f7f7f7;
#             border-radius: 10px;
#         }
#         .filter-group {
#             display: flex;
#             flex-direction: column;
#             gap: 5px;
#         }
#         .filter-group label {
#             font-weight: bold;
#             color: #555;
#             font-size: 14px;
#         }
#         .filter-group input, .filter-group select {
#             padding: 8px;
#             border: 1px solid #ddd;
#             border-radius: 5px;
#         }
#         .result-item {
#             padding: 15px;
#             border-bottom: 1px solid #eee;
#             transition: 0.3s;
#         }
#         .result-item:hover {
#             background: #f9f9f9;
#         }
#         .result-title {
#             font-size: 18px;
#             font-weight: bold;
#             color: #667eea;
#             margin-bottom: 5px;
#         }
#         .result-meta {
#             font-size: 12px;
#             color: #888;
#             margin-bottom: 10px;
#         }
#         .result-snippet {
#             color: #555;
#             line-height: 1.5;
#         }
#         .result-count {
#             background: #667eea;
#             color: white;
#             padding: 5px 10px;
#             border-radius: 20px;
#             font-size: 12px;
#             display: inline-block;
#             margin-bottom: 15px;
#         }
#         .highlight {
#             background: yellow;
#             font-weight: bold;
#         }
#         .pagination {
#             display: flex;
#             justify-content: center;
#             gap: 10px;
#             margin-top: 20px;
#             align-items: center;
#         }
#         .pagination button {
#             padding: 8px 15px;
#             background: #667eea;
#             color: white;
#             border: none;
#             border-radius: 5px;
#             cursor: pointer;
#         }
#         .pagination button:disabled {
#             background: #ccc;
#             cursor: not-allowed;
#         }
#         .stats-grid {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
#             gap: 15px;
#         }
#         .stat-card {
#             background: #f7f7f7;
#             padding: 15px;
#             border-radius: 10px;
#             text-align: center;
#         }
#         .stat-number {
#             font-size: 32px;
#             font-weight: bold;
#             color: #667eea;
#         }
#         .format-checkbox {
#             display: inline-block;
#             margin-right: 15px;
#             margin-bottom: 10px;
#         }
#         button {
#             background: #667eea;
#             color: white;
#             border: none;
#             padding: 10px 20px;
#             border-radius: 5px;
#             cursor: pointer;
#             margin: 5px;
#         }
#         button:hover {
#             background: #5a67d8;
#         }
#         .suggestion {
#             background: #fff3cd;
#             border-left: 4px solid #ffc107;
#             padding: 10px;
#             margin-bottom: 20px;
#             border-radius: 5px;
#         }
#         .nav-tabs {
#             display: flex;
#             gap: 10px;
#             margin-bottom: 20px;
#             border-bottom: 2px solid #ddd;
#         }
#         .tab {
#             padding: 10px 20px;
#             cursor: pointer;
#             border: none;
#             background: none;
#         }
#         .tab.active {
#             color: #667eea;
#             border-bottom: 2px solid #667eea;
#         }
#         .tab-content {
#             display: none;
#         }
#         .tab-content.active {
#             display: block;
#         }
#         .message {
#             padding: 10px;
#             border-radius: 5px;
#             margin-bottom: 15px;
#         }
#         .message.success {
#             background: #d4edda;
#             color: #155724;
#             border: 1px solid #c3e6cb;
#         }
#         .message.error {
#             background: #f8d7da;
#             color: #721c24;
#             border: 1px solid #f5c6cb;
#         }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="card">
#             <h1>🔍 Mini Search Engine</h1>
#             <p>Index and search your documents with boolean, phrase, fuzzy, and wildcard queries</p>
            
#             <div class="nav-tabs">
#                 <button class="tab active" onclick="showTab('search')">🔎 Search</button>
#                 <button class="tab" onclick="showTab('build')">📚 Build Index</button>
#                 <button class="tab" onclick="showTab('stats')">📊 Statistics</button>
#             </div>
            
#             <!-- Build Index Tab -->
#             <div id="build-tab" class="tab-content active">
#                 <h3>Build Document Index</h3>
#                 <div id="build-message"></div>
#                 <div class="filters">
#                     <div class="filter-group">
#                         <label>Select file formats to index:</label>
#                         <div>
#                             <label class="format-checkbox"><input type="checkbox" value=".txt" class="format-check"> TXT</label>
#                             <label class="format-checkbox"><input type="checkbox" value=".pdf" class="format-check"> PDF</label>
#                             <label class="format-checkbox"><input type="checkbox" value=".json" class="format-check"> JSON</label>
#                             <label class="format-checkbox"><input type="checkbox" value=".csv" class="format-check"> CSV</label>
#                             <label class="format-checkbox"><input type="checkbox" value=".xlsx" class="format-check"> Excel</label>
#                         </div>
#                     </div>
#                     <div class="filter-group">
#                         <label>Folder path:</label>
#                         <input type="text" id="folder-path" placeholder="data" value="data">
#                     </div>
#                 </div>
#                 <button onclick="buildIndex()">🚀 Build / Refresh Index</button>
#             </div>
            
#             <!-- Search Tab -->
#             <div id="search-tab" class="tab-content">
#                 <div class="search-box">
#                     <input type="text" id="query" placeholder='Try: "information retrieval" OR cat~ OR comp*' >
#                     <button onclick="search()">🔍 Search</button>
#                 </div>
                
#                 <div class="filters">
#                     <div class="filter-group">
#                         <label>Date from:</label>
#                         <input type="date" id="date-from">
#                     </div>
#                     <div class="filter-group">
#                         <label>Date to:</label>
#                         <input type="date" id="date-to">
#                     </div>
#                     <div class="filter-group">
#                         <label>File type:</label>
#                         <select id="file-type">
#                             <option value="">All types</option>
#                             <option value="TXT">TXT</option>
#                             <option value="PDF">PDF</option>
#                             <option value="JSON">JSON</option>
#                             <option value="CSV">CSV</option>
#                             <option value="XLSX">Excel</option>
#                         </select>
#                     </div>
#                 </div>
                
#                 <div id="suggestion" class="suggestion" style="display:none;"></div>
#                 <div id="results"></div>
#                 <div id="pagination" class="pagination"></div>
#             </div>
            
#             <!-- Stats Tab -->
#             <div id="stats-tab" class="tab-content">
#                 <div id="stats-content"></div>
#             </div>
#         </div>
#     </div>
    
#     <script>
#         let currentResults = [];
#         let currentPage = 0;
#         let resultsPerPage = 5;
        
#         function showTab(tabName) {
#             document.querySelectorAll('.tab-content').forEach(tab => {
#                 tab.classList.remove('active');
#             });
#             document.getElementById(tabName + '-tab').classList.add('active');
            
#             document.querySelectorAll('.tab').forEach(tab => {
#                 tab.classList.remove('active');
#             });
#             event.target.classList.add('active');
            
#             if (tabName === 'stats') {
#                 loadStats();
#             }
#         }
        
#         async function buildIndex() {
#             const formats = Array.from(document.querySelectorAll('.format-check:checked'))
#                 .map(cb => cb.value);
            
#             if (formats.length === 0) {
#                 showMessage('build-message', 'Please select at least one format', 'error');
#                 return;
#             }
            
#             const folder = document.getElementById('folder-path').value;
            
#             showMessage('build-message', 'Building index... please wait', 'success');
            
#             const response = await fetch('/build', {
#                 method: 'POST',
#                 headers: {'Content-Type': 'application/json'},
#                 body: JSON.stringify({formats: formats, folder: folder})
#             });
            
#             const data = await response.json();
#             if (data.success) {
#                 showMessage('build-message', data.message, 'success');
#                 setTimeout(() => loadStats(), 1000);
#             } else {
#                 showMessage('build-message', data.message, 'error');
#             }
#         }
        
#         async function search() {
#             const query = document.getElementById('query').value;
#             if (!query) {
#                 alert('Please enter a search query');
#                 return;
#             }
            
#             const dateFrom = document.getElementById('date-from').value;
#             const dateTo = document.getElementById('date-to').value;
#             const fileType = document.getElementById('file-type').value;
            
#             const response = await fetch('/search', {
#                 method: 'POST',
#                 headers: {'Content-Type': 'application/json'},
#                 body: JSON.stringify({
#                     query: query,
#                     date_from: dateFrom,
#                     date_to: dateTo,
#                     file_type: fileType
#                 })
#             });
            
#             const data = await response.json();
            
#             if (data.suggestion) {
#                 const suggestionDiv = document.getElementById('suggestion');
#                 suggestionDiv.style.display = 'block';
#                 suggestionDiv.innerHTML = `💡 Did you mean: <strong>${data.suggestion}</strong>? 
#                     <button onclick="document.getElementById('query').value='${data.suggestion}'; search()">Try this</button>`;
#             } else {
#                 document.getElementById('suggestion').style.display = 'none';
#             }
            
#             currentResults = data.results || [];
#             currentPage = 0;
#             displayResults();
#         }
        
#         function displayResults() {
#             const resultsDiv = document.getElementById('results');
#             const paginationDiv = document.getElementById('pagination');
            
#             if (currentResults.length === 0) {
#                 resultsDiv.innerHTML = '<p>❌ No results found</p>';
#                 paginationDiv.innerHTML = '';
#                 return;
#             }
            
#             const start = currentPage * resultsPerPage;
#             const end = start + resultsPerPage;
#             const pageResults = currentResults.slice(start, end);
#             const totalPages = Math.ceil(currentResults.length / resultsPerPage);
            
#             // Show result count
#             let html = `<div class="result-count">📊 Found ${currentResults.length} total results</div>`;
            
#             html += pageResults.map(result => `
#                 <div class="result-item">
#                     <div class="result-title">📄 ${escapeHtml(result.filename)}</div>
#                     <div class="result-meta">
#                         Type: ${result.type} | Score: ${result.score} | 
#                         Modified: ${result.date}
#                     </div>
#                     <div class="result-snippet">${result.snippet || 'No preview available'}</div>
#                 </div>
#             `).join('');
            
#             resultsDiv.innerHTML = html;
            
#             // Show pagination if more than 1 page
#             if (totalPages > 1) {
#                 paginationDiv.innerHTML = `
#                     <button onclick="changePage(-1)" ${currentPage === 0 ? 'disabled' : ''}>◀ Previous</button>
#                     <span>Page ${currentPage + 1} of ${totalPages}</span>
#                     <button onclick="changePage(1)" ${currentPage === totalPages - 1 ? 'disabled' : ''}>Next ▶</button>
#                 `;
#             } else {
#                 paginationDiv.innerHTML = '';
#             }
#         }
        
#         function changePage(delta) {
#             const newPage = currentPage + delta;
#             const totalPages = Math.ceil(currentResults.length / resultsPerPage);
            
#             if (newPage >= 0 && newPage < totalPages) {
#                 currentPage = newPage;
#                 displayResults();
#             }
#         }
        
#         function escapeHtml(text) {
#             const div = document.createElement('div');
#             div.textContent = text;
#             return div.innerHTML;
#         }
        
#         async function loadStats() {
#             const response = await fetch('/stats');
#             const stats = await response.json();
            
#             const statsDiv = document.getElementById('stats-content');
#             statsDiv.innerHTML = `
#                 <div class="stats-grid">
#                     <div class="stat-card">
#                         <div class="stat-number">${stats.total_docs}</div>
#                         <div>Total Documents</div>
#                     </div>
#                     <div class="stat-card">
#                         <div class="stat-number">${stats.unique_terms}</div>
#                         <div>Unique Terms</div>
#                     </div>
#                 </div>
#                 <h3>📁 Documents by Type</h3>
#                 <div class="stats-grid">
#                     ${Object.entries(stats.type_breakdown || {}).map(([type, count]) => `
#                         <div class="stat-card">
#                             <div class="stat-number">${count}</div>
#                             <div>${type}</div>
#                         </div>
#                     `).join('')}
#                 </div>
#                 <h3>🔥 Top 10 Most Frequent Terms</h3>
#                 <div class="stats-grid">
#                     ${(stats.top_terms || []).map(term => `
#                         <div class="stat-card">
#                             <div class="stat-number">${term[1]}</div>
#                             <div>"${term[0]}"</div>
#                         </div>
#                     `).join('')}
#                 </div>
#             `;
#         }
        
#         function showMessage(elementId, message, type) {
#             const div = document.getElementById(elementId);
#             div.innerHTML = `<div class="message ${type}">${message}</div>`;
#             setTimeout(() => {
#                 div.innerHTML = '';
#             }, 3000);
#         }
#     </script>
# </body>
# </html>
# '''

# @app.route('/')
# def index():
#     return render_template_string(HTML_TEMPLATE)

# @app.route('/build', methods=['POST'])
# def build_index():
#     global search_engine, indexer
#     data = request.json
    
#     indexer.selected_formats = data['formats']
#     folder = data.get('folder', 'data')
    
#     success = indexer.build_index(folder)
    
#     if success:
#         search_engine = SearchEngine(indexer)
#         return jsonify({
#             'success': True,
#             'message': f'Indexed {indexer.doc_counter} files successfully!'
#         })
#     else:
#         return jsonify({
#             'success': False,
#             'message': 'Failed to build index. Check folder path.'
#         })

# @app.route('/search', methods=['POST'])
# def search():
#     global search_engine
#     data = request.json
    
#     if not search_engine:
#         return jsonify({'results': [], 'suggestion': None})
    
#     # Parse date filters
#     date_from = datetime.strptime(data['date_from'], '%Y-%m-%d') if data.get('date_from') else None
#     date_to = datetime.strptime(data['date_to'], '%Y-%m-%d') if data.get('date_to') else None
#     file_type = [data['file_type']] if data.get('file_type') else None
    
#     results = search_engine.search(data['query'], date_from, date_to, file_type)
    
#     # Format ALL results for display (NO LIMIT - removed [:50])
#     formatted_results = []
#     for doc_id, score in results:  # ← REMOVED [:50] - NOW SHOWS ALL RESULTS
#         doc = search_engine.indexer.documents[doc_id]
        
#         # Get highlighted snippet
#         query_terms = data['query'].lower().split()
#         snippet = search_engine.get_snippet(doc_id, query_terms, 200)
        
#         formatted_results.append({
#             'filename': doc['filename'],
#             'type': doc['type'],
#             'score': score,
#             'date': doc['date'],
#             'snippet': snippet
#         })
    
#     # Get suggestion if no results
#     suggestion = None
#     if not results:
#         suggestion = search_engine.did_you_mean(data['query'])
    
#     return jsonify({
#         'results': formatted_results,
#         'suggestion': suggestion
#     })

# @app.route('/stats')
# def stats():
#     global indexer
#     if indexer.doc_counter == 0:
#         return jsonify({'total_docs': 0, 'type_breakdown': {}, 'top_terms': []})
    
#     # Type breakdown
#     type_counts = {}
#     for doc in indexer.documents.values():
#         t = doc['type']
#         type_counts[t] = type_counts.get(t, 0) + 1
    
#     # Top terms by TOTAL OCCURRENCES
#     term_counts = []
#     for word, docs in indexer.inverted_index.items():
#         total = 0
#         for positions in docs.values():
#             total += len(positions)
#         term_counts.append((word, total))
    
#     term_counts.sort(key=lambda x: x[1], reverse=True)
#     top_terms = term_counts[:10]
    
#     return jsonify({
#         'total_docs': indexer.doc_counter,
#         'unique_terms': len(indexer.inverted_index),
#         'type_breakdown': type_counts,
#         'top_terms': [(word, count) for word, count in top_terms]
#     })

# if __name__ == '__main__':
#     # Load existing index if available
#     if indexer.load_index():
#         search_engine = SearchEngine(indexer)
#         print("✅ Loaded existing index!")
    
#     print("\n🚀 Starting web server...")
#     print("🌐 Open your browser and go to: http://localhost:5000")
#     app.run(debug=True)














# web_app.py - Web-based UI using Flask (FIXED PAGINATION)
from flask import Flask, render_template_string, request, jsonify
from indexer import Indexer
from search import SearchEngine
from datetime import datetime
import os

app = Flask(__name__)

# Global search engine instance
search_engine = None
indexer = Indexer()

# HTML Template with built-in UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔍 Mini Search Engine</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .search-box input {
            flex: 1;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 10px;
            transition: 0.3s;
        }
        .search-box input:focus {
            outline: none;
            border-color: #667eea;
        }
        .search-box button {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
        }
        .search-box button:hover {
            background: #5a67d8;
        }
        .filters {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f7f7f7;
            border-radius: 10px;
        }
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .filter-group label {
            font-weight: bold;
            color: #555;
            font-size: 14px;
        }
        .filter-group input, .filter-group select {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .result-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            transition: 0.3s;
        }
        .result-item:hover {
            background: #f9f9f9;
        }
        .result-title {
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .result-meta {
            font-size: 12px;
            color: #888;
            margin-bottom: 10px;
        }
        .result-snippet {
            color: #555;
            line-height: 1.5;
        }
        .result-count {
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            display: inline-block;
            margin-bottom: 15px;
        }
        .highlight {
            background: yellow;
            font-weight: bold;
        }
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
            align-items: center;
        }
        .pagination button {
            padding: 8px 15px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .pagination button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .stat-card {
            background: #f7f7f7;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .format-checkbox {
            display: inline-block;
            margin-right: 15px;
            margin-bottom: 10px;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover {
            background: #5a67d8;
        }
        .suggestion {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ddd;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
        }
        .tab.active {
            color: #667eea;
            border-bottom: 2px solid #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .message {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🔍 Mini Search Engine</h1>
            <p>Index and search your documents with boolean, phrase, fuzzy, and wildcard queries</p>
            
            <div class="nav-tabs">
                <button class="tab active" onclick="showTab('search')">🔎 Search</button>
                <button class="tab" onclick="showTab('build')">📚 Build Index</button>
                <button class="tab" onclick="showTab('stats')">📊 Statistics</button>
            </div>
            
            <!-- Build Index Tab -->
            <div id="build-tab" class="tab-content active">
                <h3>Build Document Index</h3>
                <div id="build-message"></div>
                <div class="filters">
                    <div class="filter-group">
                        <label>Select file formats to index:</label>
                        <div>
                            <label class="format-checkbox"><input type="checkbox" value=".txt" class="format-check"> TXT</label>
                            <label class="format-checkbox"><input type="checkbox" value=".pdf" class="format-check"> PDF</label>
                            <label class="format-checkbox"><input type="checkbox" value=".json" class="format-check"> JSON</label>
                            <label class="format-checkbox"><input type="checkbox" value=".csv" class="format-check"> CSV</label>
                            <label class="format-checkbox"><input type="checkbox" value=".xlsx" class="format-check"> Excel</label>
                        </div>
                    </div>
                    <div class="filter-group">
                        <label>Folder path:</label>
                        <input type="text" id="folder-path" placeholder="data" value="data">
                    </div>
                </div>
                <button onclick="buildIndex()">🚀 Build / Refresh Index</button>
            </div>
            
            <!-- Search Tab -->
            <div id="search-tab" class="tab-content">
                <div class="search-box">
                    <input type="text" id="query" placeholder='Try: "information retrieval" OR cat~ OR comp*' >
                    <button onclick="search()">🔍 Search</button>
                </div>
                
                <div class="filters">
                    <div class="filter-group">
                        <label>Date from:</label>
                        <input type="date" id="date-from">
                    </div>
                    <div class="filter-group">
                        <label>Date to:</label>
                        <input type="date" id="date-to">
                    </div>
                    <div class="filter-group">
                        <label>File type:</label>
                        <select id="file-type">
                            <option value="">All types</option>
                            <option value="TXT">TXT</option>
                            <option value="PDF">PDF</option>
                            <option value="JSON">JSON</option>
                            <option value="CSV">CSV</option>
                            <option value="XLSX">Excel</option>
                        </select>
                    </div>
                </div>
                
                <div id="suggestion" class="suggestion" style="display:none;"></div>
                <div id="results"></div>
                <div id="pagination" class="pagination"></div>
            </div>
            
            <!-- Stats Tab -->
            <div id="stats-tab" class="tab-content">
                <div id="stats-content"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentResults = [];
        let currentPage = 0;
        let resultsPerPage = 5;
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName + '-tab').classList.add('active');
            
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            if (tabName === 'stats') {
                loadStats();
            }
        }
        
        async function buildIndex() {
            const formats = Array.from(document.querySelectorAll('.format-check:checked'))
                .map(cb => cb.value);
            
            if (formats.length === 0) {
                showMessage('build-message', 'Please select at least one format', 'error');
                return;
            }
            
            const folder = document.getElementById('folder-path').value;
            
            showMessage('build-message', 'Building index... please wait', 'success');
            
            const response = await fetch('/build', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({formats: formats, folder: folder})
            });
            
            const data = await response.json();
            if (data.success) {
                showMessage('build-message', data.message, 'success');
                setTimeout(() => loadStats(), 1000);
            } else {
                showMessage('build-message', data.message, 'error');
            }
        }
        
        async function search() {
            const query = document.getElementById('query').value;
            if (!query) {
                alert('Please enter a search query');
                return;
            }
            
            const dateFrom = document.getElementById('date-from').value;
            const dateTo = document.getElementById('date-to').value;
            const fileType = document.getElementById('file-type').value;
            
            const response = await fetch('/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    query: query,
                    date_from: dateFrom,
                    date_to: dateTo,
                    file_type: fileType
                })
            });
            
            const data = await response.json();
            
            if (data.suggestion) {
                const suggestionDiv = document.getElementById('suggestion');
                suggestionDiv.style.display = 'block';
                suggestionDiv.innerHTML = `💡 Did you mean: <strong>${data.suggestion}</strong>? 
                    <button onclick="document.getElementById('query').value='${data.suggestion}'; search()">Try this</button>`;
            } else {
                document.getElementById('suggestion').style.display = 'none';
            }
            
            currentResults = data.results || [];
            currentPage = 0;
            displayResults();
        }
        
        function displayResults() {
            const resultsDiv = document.getElementById('results');
            const paginationDiv = document.getElementById('pagination');
            
            if (currentResults.length === 0) {
                resultsDiv.innerHTML = '<p>❌ No results found</p>';
                paginationDiv.innerHTML = '';
                return;
            }
            
            const start = currentPage * resultsPerPage;
            const end = start + resultsPerPage;
            const pageResults = currentResults.slice(start, end);
            const totalPages = Math.ceil(currentResults.length / resultsPerPage);
            
            // Show result count
            let html = `<div class="result-count">📊 Found ${currentResults.length} results</div>`;
            
            html += pageResults.map(result => `
                <div class="result-item">
                    <div class="result-title">📄 ${escapeHtml(result.filename)}</div>
                    <div class="result-meta">
                        Type: ${result.type} | Score: ${result.score} | 
                        Modified: ${result.date}
                    </div>
                    <div class="result-snippet">${result.snippet || 'No preview available'}</div>
                </div>
            `).join('');
            
            resultsDiv.innerHTML = html;
            
            // Only show pagination if more than one page
            if (totalPages > 1) {
                paginationDiv.innerHTML = `
                    <button onclick="changePage(-1)" id="prevBtn" ${currentPage === 0 ? 'disabled' : ''}>◀ Previous</button>
                    <span>Page ${currentPage + 1} of ${totalPages}</span>
                    <button onclick="changePage(1)" id="nextBtn" ${currentPage === totalPages - 1 ? 'disabled' : ''}>Next ▶</button>
                `;
            } else {
                paginationDiv.innerHTML = '';
            }
        }
        
        function changePage(delta) {
            const newPage = currentPage + delta;
            const totalPages = Math.ceil(currentResults.length / resultsPerPage);
            
            if (newPage >= 0 && newPage < totalPages) {
                currentPage = newPage;
                displayResults();
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function loadStats() {
            const response = await fetch('/stats');
            const stats = await response.json();
            
            const statsDiv = document.getElementById('stats-content');
            statsDiv.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${stats.total_docs}</div>
                        <div>Total Documents</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.unique_terms}</div>
                        <div>Unique Terms</div>
                    </div>
                </div>
                <h3>📁 Documents by Type</h3>
                <div class="stats-grid">
                    ${Object.entries(stats.type_breakdown || {}).map(([type, count]) => `
                        <div class="stat-card">
                            <div class="stat-number">${count}</div>
                            <div>${type}</div>
                        </div>
                    `).join('')}
                </div>
                <h3>🔥 Top 10 Most Frequent Terms (Total Occurrences)</h3>
                <div class="stats-grid">
                    ${(stats.top_terms || []).map(term => `
                        <div class="stat-card">
                            <div class="stat-number">${term[1]}</div>
                            <div>"${term[0]}"</div>
                            <div style="font-size: 10px; color: #888; margin-top: 5px;">total times found</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        function showMessage(elementId, message, type) {
            const div = document.getElementById(elementId);
            div.innerHTML = `<div class="message ${type}">${message}</div>`;
            setTimeout(() => {
                div.innerHTML = '';
            }, 3000);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/build', methods=['POST'])
def build_index():
    global search_engine, indexer
    data = request.json
    
    indexer.selected_formats = data['formats']
    folder = data.get('folder', 'data')
    
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
            'message': 'Failed to build index. Check folder path.'
        })

@app.route('/search', methods=['POST'])
def search():
    global search_engine
    data = request.json
    
    if not search_engine:
        return jsonify({'results': [], 'suggestion': None})
    
    # Parse date filters
    date_from = datetime.strptime(data['date_from'], '%Y-%m-%d') if data.get('date_from') else None
    date_to = datetime.strptime(data['date_to'], '%Y-%m-%d') if data.get('date_to') else None
    file_type = [data['file_type']] if data.get('file_type') else None
    
    results = search_engine.search(data['query'], date_from, date_to, file_type)
    
    # Format ALL results for display (NO LIMIT)
    formatted_results = []
    for doc_id, score in results:  # ← NO LIMIT - ALL results
        doc = search_engine.indexer.documents[doc_id]
        
        # Get highlighted snippet
        query_terms = data['query'].lower().split()
        snippet = search_engine.get_snippet(doc_id, query_terms, 200)
        
        formatted_results.append({
            'filename': doc['filename'],
            'type': doc['type'],
            'score': score,
            'date': doc['date'],
            'snippet': snippet
        })
    
    # Get suggestion if no results
    suggestion = None
    if not results:
        suggestion = search_engine.did_you_mean(data['query'])
    
    return jsonify({
        'results': formatted_results,  # ← ALL results sent to frontend
        'suggestion': suggestion
    })

@app.route('/stats')
def stats():
    global indexer
    if indexer.doc_counter == 0:
        return jsonify({'total_docs': 0, 'type_breakdown': {}, 'top_terms': []})
    
    # Type breakdown
    type_counts = {}
    for doc in indexer.documents.values():
        t = doc['type']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    # Top terms by TOTAL occurrences (not just document count)
    term_counts = []
    for word, docs in indexer.inverted_index.items():
        total = 0
        for positions in docs.values():
            total += len(positions)  # Count each occurrence
        term_counts.append((word, total))
    
    term_counts.sort(key=lambda x: x[1], reverse=True)
    top_terms = term_counts[:10]
    
    return jsonify({
        'total_docs': indexer.doc_counter,
        'unique_terms': len(indexer.inverted_index),
        'type_breakdown': type_counts,
        'top_terms': [(word, count) for word, count in top_terms]
    })

if __name__ == '__main__':
    # Load existing index if available
    if indexer.load_index():
        search_engine = SearchEngine(indexer)
        print("✅ Loaded existing index!")
    
    print("\n🚀 Starting web server...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    app.run(debug=True)













