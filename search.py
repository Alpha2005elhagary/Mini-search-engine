# # search.py - Handle all search queries
# import re
# from datetime import datetime
# from difflib import get_close_matches

# class SearchEngine:
#     def __init__(self, indexer):
#         self.indexer = indexer
#         self.current_results = []
    
#     def search(self, query, date_from=None, date_to=None, file_types=None):
#         """Main search function"""
#         if not self.indexer.inverted_index:
#             print("❌ No index loaded! Build index first.")
#             return []
        
#         # Parse the query
#         parsed = self.parse_query(query)
        
#         if not parsed:
#             return []
        
#         # Get initial results
#         results = self.execute_query(parsed)
        
#         # Apply filters
#         results = self.apply_filters(results, date_from, date_to, file_types)
        
#         # Calculate scores and sort
#         results = self.score_results(results)
        
#         self.current_results = results
#         return results
    
#     def parse_query(self, query):
#         """Simple manual parser for boolean, phrase, wildcard, fuzzy"""
#         query = query.strip()
        
#         # Handle phrase queries (words in quotes)
#         phrases = re.findall(r'"([^"]+)"', query)
#         for phrase in phrases:
#             query = query.replace(f'"{phrase}"', f'PHRASE({phrase})')
        
#         # Handle fuzzy queries (word~)
#         def replace_fuzzy(match):
#             word = match.group(1)
#             return f'FUZZY({word})'
        
#         query = re.sub(r'(\w+)~(\d*)?', replace_fuzzy, query)
        
#         # Handle wildcard (inform*, ?earch)
#         # We'll handle these separately
        
#         # Parse boolean with parentheses (simplified)
#         # For now, split by spaces but respect our markers
#         tokens = []
#         current = []
#         depth = 0
        
#         for char in query + " ":
#             if char == '(':
#                 depth += 1
#                 current.append(char)
#             elif char == ')':
#                 depth -= 1
#                 current.append(char)
#             elif char == ' ' and depth == 0 and current:
#                 tokens.append(''.join(current))
#                 current = []
#             else:
#                 current.append(char)
        
#         # Process tokens
#         parsed = []
#         for token in tokens[:-1] if tokens[-1] == '' else tokens:
#             if token.upper() == 'AND':
#                 parsed.append(('OP', 'AND'))
#             elif token.upper() == 'OR':
#                 parsed.append(('OP', 'OR'))
#             elif token.upper() == 'NOT':
#                 parsed.append(('OP', 'NOT'))
#             elif token.startswith('PHRASE('):
#                 phrase = token[7:-1]
#                 parsed.append(('PHRASE', phrase))
#             elif token.startswith('FUZZY('):
#                 word = token[6:-1]
#                 parsed.append(('FUZZY', word))
#             else:
#                 # Check for wildcard
#                 if '*' in token or '?' in token:
#                     parsed.append(('WILDCARD', token))
#                 else:
#                     parsed.append(('TERM', token.lower()))
        
#         return parsed
    
#     def execute_query(self, parsed):
#         """Execute parsed query and return doc sets"""
#         if not parsed:
#             return set()
        
#         results = []
        
#         # Simple evaluation (left to right)
#         current_set = None
#         current_op = None
        
#         for token_type, value in parsed:
#             if token_type == 'OP':
#                 current_op = value
#             else:
#                 # Get docs for this token
#                 docs = self.get_docs_for_token(token_type, value)
                
#                 if current_set is None:
#                     current_set = docs
#                 elif current_op == 'AND':
#                     current_set = current_set.intersection(docs)
#                 elif current_op == 'OR':
#                     current_set = current_set.union(docs)
#                 elif current_op == 'NOT':
#                     current_set = current_set.difference(docs)
        
#         return list(current_set) if current_set else []
    
#     def get_docs_for_token(self, token_type, value):
#         """Get documents for a single query token"""
#         if token_type == 'TERM':
#             return set(self.indexer.inverted_index.get(value, {}).keys())
        
#         elif token_type == 'PHRASE':
#             return self.phrase_search(value)
        
#         elif token_type == 'FUZZY':
#             return self.fuzzy_search(value)
        
#         elif token_type == 'WILDCARD':
#             return self.wildcard_search(value)
        
#         return set()
    
#     def phrase_search(self, phrase):
#         """Find exact phrase matches"""
#         words = phrase.lower().split()
#         if not words:
#             return set()
        
#         # Get docs containing first word
#         first_word_docs = self.indexer.inverted_index.get(words[0], {})
        
#         matching_docs = set()
        
#         for doc_id, positions in first_word_docs.items():
#             content = self.indexer.documents[doc_id]['content'].lower()
            
#             # Check if phrase exists in content
#             if phrase.lower() in content:
#                 matching_docs.add(doc_id)
        
#         return matching_docs
    
#     def fuzzy_search(self, term, max_distance=2):
#         """Fuzzy search using Levenshtein-like matching"""
#         term = term.lower()
#         matches = set()
        
#         # Find words in index similar to the term
#         all_words = list(self.indexer.inverted_index.keys())
        
#         for word in all_words:
#             distance = self.levenshtein_distance(term, word)
#             if distance <= max_distance:
#                 matches.update(self.indexer.inverted_index[word].keys())
        
#         return matches
    
#     def levenshtein_distance(self, s1, s2):
#         """Simple Levenshtein distance"""
#         if len(s1) < len(s2):
#             return self.levenshtein_distance(s2, s1)
        
#         if len(s2) == 0:
#             return len(s1)
        
#         previous_row = list(range(len(s2) + 1))
#         for i, c1 in enumerate(s1):
#             current_row = [i + 1]
#             for j, c2 in enumerate(s2):
#                 insertions = previous_row[j + 1] + 1
#                 deletions = current_row[j] + 1
#                 substitutions = previous_row[j] + (c1 != c2)
#                 current_row.append(min(insertions, deletions, substitutions))
#             previous_row = current_row
        
#         return previous_row[-1]
    
#     def wildcard_search(self, pattern):
#         """Wildcard matching (* and ?)"""
#         pattern = pattern.lower()
        
#         # Convert to regex
#         regex_pattern = pattern.replace('*', '.*').replace('?', '.')
#         regex = re.compile(f'^{regex_pattern}$')
        
#         matches = set()
#         for word in self.indexer.inverted_index.keys():
#             if regex.match(word):
#                 matches.update(self.indexer.inverted_index[word].keys())
        
#         return matches
    
#     def apply_filters(self, results, date_from, date_to, file_types):
#         """Apply date range and file type filters"""
#         if not results:
#             return results
        
#         filtered = []
        
#         for doc_id in results:
#             doc = self.indexer.documents[doc_id]
            
#             # Date filter
#             if date_from or date_to:
#                 doc_date = datetime.fromtimestamp(doc['timestamp'])
#                 if date_from and doc_date < date_from:
#                     continue
#                 if date_to and doc_date > date_to:
#                     continue
            
#             # File type filter
#             if file_types and doc['type'] not in file_types:
#                 continue
            
#             filtered.append(doc_id)
        
#         return filtered
    
#     def score_results(self, results):
#         """Score results by term frequency"""
#         scored = []
#         for doc_id in results:
#             # Simple scoring: more matches = higher score
#             score = 0
#             for term, posting in self.indexer.inverted_index.items():
#                 if doc_id in posting:
#                     score += len(posting[doc_id])
#             scored.append((doc_id, score))
        
#         scored.sort(key=lambda x: x[1], reverse=True)
#         return scored
    
#     def get_snippet(self, doc_id, query_terms, max_length=150):
#         """Get highlighted snippet around matching terms"""
#         content = self.indexer.documents[doc_id]['content']
#         words = content.split()
        
#         # Find best snippet position
#         best_pos = 0
#         max_matches = 0
        
#         for i, word in enumerate(words):
#             matches = sum(1 for term in query_terms if term.lower() in word.lower())
#             if matches > max_matches:
#                 max_matches = matches
#                 best_pos = i
        
#         # Extract snippet
#         start = max(0, best_pos - 20)
#         end = min(len(words), best_pos + 20)
#         snippet = ' '.join(words[start:end])
        
#         # Highlight matches
#         for term in query_terms:
#             snippet = re.sub(f'({term})', r'**\1**', snippet, flags=re.IGNORECASE)
        
#         if len(snippet) > max_length:
#             snippet = snippet[:max_length] + "..."
        
#         return snippet
    
#     def did_you_mean(self, query):
#         """Suggest correction when no results"""
#         words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
        
#         all_index_words = list(self.indexer.inverted_index.keys())
        
#         suggestions = []
#         for word in words:
#             matches = get_close_matches(word, all_index_words, n=1, cutoff=0.7)
#             if matches:
#                 suggestions.append(matches[0])
#             else:
#                 suggestions.append(word)
        
#         if suggestions != words:
#             return ' '.join(suggestions)
#         return None












# # search.py - Handle all search queries (FULLY FIXED)
# import re
# from datetime import datetime
# from difflib import get_close_matches

# class SearchEngine:
#     def __init__(self, indexer):
#         self.indexer = indexer
#         self.current_results = []
    
#     def search(self, query, date_from=None, date_to=None, file_types=None):
#         """Main search function"""
#         if not self.indexer.inverted_index:
#             print("❌ No index loaded! Build index first.")
#             return []
        
#         # Parse the query
#         parsed = self.parse_query(query)
        
#         if not parsed:
#             return []
        
#         # Get initial results
#         results = self.execute_query(parsed)
        
#         # Apply filters
#         results = self.apply_filters(results, date_from, date_to, file_types)
        
#         # Calculate scores and sort
#         results = self.score_results(results)
        
#         self.current_results = results
#         return results
    
#     def parse_query(self, query):
#         """Parse boolean queries with parentheses support (Shunting Yard algorithm)"""
#         query = query.strip()
        
#         # Handle phrase queries (words in quotes)
#         phrases = re.findall(r'"([^"]+)"', query)
#         for phrase in phrases:
#             query = query.replace(f'"{phrase}"', f'PHRASE({phrase})')
        
#         # Handle fuzzy queries (word~)
#         def replace_fuzzy(match):
#             word = match.group(1)
#             dist = match.group(2) if match.group(2) else '2'
#             return f'FUZZY({word},{dist})'
        
#         query = re.sub(r'(\w+)~(\d*)?', replace_fuzzy, query)
        
#         # Tokenize preserving parentheses
#         tokens = []
#         current = ""
#         for char in query:
#             if char == ' ' and current:
#                 tokens.append(current)
#                 current = ""
#             elif char == '(' or char == ')':
#                 if current:
#                     tokens.append(current)
#                     current = ""
#                 tokens.append(char)
#             else:
#                 current += char
#         if current:
#             tokens.append(current)
        
#         # Convert to postfix using Shunting Yard algorithm
#         output = []
#         operators = []
#         precedence = {'AND': 2, 'OR': 1, 'NOT': 3}
        
#         for token in tokens:
#             token_upper = token.upper()
#             if token_upper in ['AND', 'OR', 'NOT']:
#                 while (operators and operators[-1] != '(' and 
#                        precedence.get(operators[-1], 0) >= precedence.get(token_upper, 0)):
#                     output.append(('OP', operators.pop()))
#                 operators.append(token_upper)
#             elif token == '(':
#                 operators.append(token)
#             elif token == ')':
#                 while operators and operators[-1] != '(':
#                     output.append(('OP', operators.pop()))
#                 if operators and operators[-1] == '(':
#                     operators.pop()
#             elif token.startswith('PHRASE('):
#                 phrase = token[7:-1]
#                 output.append(('PHRASE', phrase))
#             elif token.startswith('FUZZY('):
#                 parts = token[6:-1].split(',')
#                 word = parts[0]
#                 dist = int(parts[1]) if len(parts) > 1 and parts[1] else 2
#                 output.append(('FUZZY', word, dist))
#             elif '*' in token or '?' in token:
#                 output.append(('WILDCARD', token))
#             else:
#                 output.append(('TERM', token.lower()))
        
#         while operators:
#             output.append(('OP', operators.pop()))
        
#         return output
    
#     def execute_query(self, parsed):
#         """Execute parsed query using stack evaluation"""
#         if not parsed:
#             return set()
        
#         stack = []
        
#         for item in parsed:
#             if item[0] == 'OP':
#                 if len(stack) < 2 and item[1] != 'NOT':
#                     continue
#                 op = item[1]
#                 if op == 'NOT':
#                     if len(stack) < 1:
#                         continue
#                     right = stack.pop()
#                     all_docs = set(self.indexer.documents.keys())
#                     result = all_docs - right
#                     stack.append(result)
#                 else:
#                     right = stack.pop()
#                     left = stack.pop()
#                     if op == 'AND':
#                         result = left.intersection(right)
#                     elif op == 'OR':
#                         result = left.union(right)
#                     else:
#                         result = set()
#                     stack.append(result)
#             elif item[0] == 'TERM':
#                 docs = set(self.indexer.inverted_index.get(item[1], {}).keys())
#                 stack.append(docs)
#             elif item[0] == 'PHRASE':
#                 docs = self.phrase_search(item[1])
#                 stack.append(docs)
#             elif item[0] == 'FUZZY':
#                 word = item[1]
#                 dist = item[2] if len(item) > 2 else 2
#                 docs = self.fuzzy_search(word, dist)
#                 stack.append(docs)
#             elif item[0] == 'WILDCARD':
#                 docs = self.wildcard_search(item[1])
#                 stack.append(docs)
        
#         return list(stack[0]) if stack else set()
    
#     def get_docs_for_token(self, token_type, value, *args):
#         """Get documents for a single query token"""
#         if token_type == 'TERM':
#             return set(self.indexer.inverted_index.get(value, {}).keys())
#         elif token_type == 'PHRASE':
#             return self.phrase_search(value)
#         elif token_type == 'FUZZY':
#             dist = args[0] if args else 2
#             return self.fuzzy_search(value, dist)
#         elif token_type == 'WILDCARD':
#             return self.wildcard_search(value)
#         return set()
    
#     def phrase_search(self, phrase):
#         """Find exact phrase matches"""
#         phrase_lower = phrase.lower()
#         matching_docs = set()
        
#         for doc_id, doc in self.indexer.documents.items():
#             if phrase_lower in doc['content'].lower():
#                 matching_docs.add(doc_id)
        
#         return matching_docs
    
#     def fuzzy_search(self, term, max_distance=2):
#         """Fuzzy search using Levenshtein-like matching"""
#         term = term.lower()
#         matches = set()
        
#         # Find words in index similar to the term
#         all_words = list(self.indexer.inverted_index.keys())
        
#         for word in all_words:
#             distance = self.levenshtein_distance(term, word)
#             if distance <= max_distance:
#                 matches.update(self.indexer.inverted_index[word].keys())
        
#         return matches
    
#     def levenshtein_distance(self, s1, s2):
#         """Simple Levenshtein distance"""
#         if len(s1) < len(s2):
#             return self.levenshtein_distance(s2, s1)
        
#         if len(s2) == 0:
#             return len(s1)
        
#         previous_row = list(range(len(s2) + 1))
#         for i, c1 in enumerate(s1):
#             current_row = [i + 1]
#             for j, c2 in enumerate(s2):
#                 insertions = previous_row[j + 1] + 1
#                 deletions = current_row[j] + 1
#                 substitutions = previous_row[j] + (c1 != c2)
#                 current_row.append(min(insertions, deletions, substitutions))
#             previous_row = current_row
        
#         return previous_row[-1]
    
#     def wildcard_search(self, pattern):
#         """Wildcard matching (* and ?) including leading wildcards"""
#         pattern = pattern.lower()
        
#         # Convert to regex (handle leading/trailing *)
#         regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        
#         # If pattern starts with *, match anywhere
#         if pattern.startswith('*'):
#             regex_pattern = f'.*{regex_pattern[1:]}'
#         elif pattern.endswith('*'):
#             regex_pattern = f'{regex_pattern}.*'
        
#         regex = re.compile(f'^{regex_pattern}$')
        
#         matches = set()
#         for word in self.indexer.inverted_index.keys():
#             if regex.match(word):
#                 matches.update(self.indexer.inverted_index[word].keys())
        
#         # Also try substring matching for leading wildcard
#         if pattern.startswith('*') and len(pattern) > 2:
#             search_term = pattern[1:]
#             for word in self.indexer.inverted_index.keys():
#                 if search_term in word:
#                     matches.update(self.indexer.inverted_index[word].keys())
        
#         return matches
    
#     def apply_filters(self, results, date_from, date_to, file_types):
#         """Apply date range and file type filters"""
#         if not results:
#             return results
        
#         filtered = []
        
#         for doc_id in results:
#             doc = self.indexer.documents[doc_id]
            
#             # Date filter
#             if date_from or date_to:
#                 doc_date = datetime.fromtimestamp(doc['timestamp'])
#                 if date_from and doc_date < date_from:
#                     continue
#                 if date_to and doc_date > date_to:
#                     continue
            
#             # File type filter
#             if file_types and doc['type'] not in file_types:
#                 continue
            
#             filtered.append(doc_id)
        
#         return filtered
    
#     def score_results(self, results):
#         """Score results by term frequency"""
#         scored = []
#         for doc_id in results:
#             # Simple scoring: more matches = higher score
#             score = 0
#             for term, posting in self.indexer.inverted_index.items():
#                 if doc_id in posting:
#                     score += len(posting[doc_id])
#             scored.append((doc_id, score))
        
#         scored.sort(key=lambda x: x[1], reverse=True)
#         return scored
    
#     def get_snippet(self, doc_id, query_terms, max_length=150):
#         """Get highlighted snippet around matching terms"""
#         content = self.indexer.documents[doc_id]['content']
#         words = content.split()
        
#         # Find best snippet position
#         best_pos = 0
#         max_matches = 0
        
#         for i, word in enumerate(words):
#             matches = sum(1 for term in query_terms if term.lower() in word.lower())
#             if matches > max_matches:
#                 max_matches = matches
#                 best_pos = i
        
#         # Extract snippet
#         start = max(0, best_pos - 20)
#         end = min(len(words), best_pos + 20)
#         snippet = ' '.join(words[start:end])
        
#         # Highlight matches
#         for term in query_terms:
#             snippet = re.sub(f'({term})', r'**\1**', snippet, flags=re.IGNORECASE)
        
#         if len(snippet) > max_length:
#             snippet = snippet[:max_length] + "..."
        
#         return snippet
    
#     def did_you_mean(self, query):
#         """Suggest correction when no results"""
#         words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
        
#         all_index_words = list(self.indexer.inverted_index.keys())
        
#         suggestions = []
#         for word in words:
#             matches = get_close_matches(word, all_index_words, n=1, cutoff=0.7)
#             if matches:
#                 suggestions.append(matches[0])
#             else:
#                 suggestions.append(word)
        
#         if suggestions != words:
#             return ' '.join(suggestions)
#         return None















# # search.py - Complete working search engine for Web UI
# import re
# from datetime import datetime
# from difflib import get_close_matches

# class SearchEngine:
#     def __init__(self, indexer):
#         self.indexer = indexer
#         self.current_results = []
    
#     def search(self, query, date_from=None, date_to=None, file_types=None):
#         """Main search function - supports ALL query types"""
#         if not self.indexer.inverted_index:
#             print("❌ No index loaded! Build index first.")
#             return []
        
#         try:
#             parsed = self.parse_query(query)
#             if not parsed:
#                 return []
            
#             results = self.execute_query(parsed)
#             results = self.apply_filters(results, date_from, date_to, file_types)
#             results = self.score_results(results)
#             self.current_results = results
#             return results
#         except Exception as e:
#             print(f"Search error: {e}")
#             return []
    
#     def parse_query(self, query):
#         """Parse ALL query types: boolean, phrase, fuzzy, wildcard with parentheses"""
#         query = query.strip()
        
#         # Step 1: Replace phrase queries "exact phrase" with placeholders
#         phrases = re.findall(r'"([^"]+)"', query)
#         phrase_map = {}
#         for i, phrase in enumerate(phrases):
#             placeholder = f"__PHRASE_{i}__"
#             phrase_map[placeholder] = phrase
#             query = query.replace(f'"{phrase}"', placeholder)
        
#         # Step 2: Replace fuzzy queries word~ or word~2
#         def replace_fuzzy(match):
#             word = match.group(1)
#             dist = match.group(2) if match.group(2) else '2'
#             return f'__FUZZY_{word}_{dist}__'
        
#         query = re.sub(r'(\w+)~(\d*)?', replace_fuzzy, query)
        
#         # Step 3: Tokenize (split by spaces, preserve parentheses)
#         tokens = []
#         current = ""
#         for char in query:
#             if char == ' ' and current:
#                 tokens.append(current)
#                 current = ""
#             elif char == '(' or char == ')':
#                 if current:
#                     tokens.append(current)
#                     current = ""
#                 tokens.append(char)
#             else:
#                 current += char
#         if current:
#             tokens.append(current)
        
#         # Step 4: Process each token
#         parsed = []
#         for token in tokens:
#             if token == '(':
#                 parsed.append(('LPAREN', None))
#             elif token == ')':
#                 parsed.append(('RPAREN', None))
#             elif token.upper() == 'AND':
#                 parsed.append(('OP', 'AND'))
#             elif token.upper() == 'OR':
#                 parsed.append(('OP', 'OR'))
#             elif token.upper() == 'NOT':
#                 parsed.append(('OP', 'NOT'))
#             elif token.startswith('__PHRASE_'):
#                 phrase = phrase_map.get(token, '')
#                 parsed.append(('PHRASE', phrase))
#             elif token.startswith('__FUZZY_'):
#                 parts = token.replace('__FUZZY_', '').replace('__', '').split('_')
#                 word = parts[0]
#                 dist = int(parts[1]) if len(parts) > 1 else 2
#                 parsed.append(('FUZZY', word, dist))
#             elif '*' in token or '?' in token:
#                 parsed.append(('WILDCARD', token))
#             else:
#                 parsed.append(('TERM', token.lower()))
        
#         # Step 5: Convert to postfix (RPN) for proper operator precedence
#         return self.to_postfix(parsed)
    
#     def to_postfix(self, tokens):
#         """Convert infix to postfix (Shunting Yard algorithm)"""
#         output = []
#         stack = []
#         precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
        
#         for token in tokens:
#             if token[0] in ['TERM', 'PHRASE', 'FUZZY', 'WILDCARD']:
#                 output.append(token)
#             elif token[0] == 'OP':
#                 while (stack and stack[-1][0] == 'OP' and 
#                        precedence.get(stack[-1][1], 0) >= precedence.get(token[1], 0)):
#                     output.append(stack.pop())
#                 stack.append(token)
#             elif token[0] == 'LPAREN':
#                 stack.append(token)
#             elif token[0] == 'RPAREN':
#                 while stack and stack[-1][0] != 'LPAREN':
#                     output.append(stack.pop())
#                 if stack and stack[-1][0] == 'LPAREN':
#                     stack.pop()
        
#         while stack:
#             output.append(stack.pop())
        
#         return output
    
#     def execute_query(self, parsed):
#         """Execute postfix query using stack"""
#         if not parsed:
#             return set()
        
#         stack = []
        
#         for token in parsed:
#             if token[0] == 'TERM':
#                 docs = set(self.indexer.inverted_index.get(token[1], {}).keys())
#                 stack.append(docs)
#             elif token[0] == 'PHRASE':
#                 docs = self.phrase_search(token[1])
#                 stack.append(docs)
#             elif token[0] == 'FUZZY':
#                 docs = self.fuzzy_search(token[1], token[2])
#                 stack.append(docs)
#             elif token[0] == 'WILDCARD':
#                 docs = self.wildcard_search(token[1])
#                 stack.append(docs)
#             elif token[0] == 'OP':
#                 if token[1] == 'NOT':
#                     if len(stack) >= 1:
#                         right = stack.pop()
#                         all_docs = set(self.indexer.documents.keys())
#                         result = all_docs - right
#                         stack.append(result)
#                 else:
#                     if len(stack) >= 2:
#                         right = stack.pop()
#                         left = stack.pop()
#                         if token[1] == 'AND':
#                             result = left.intersection(right)
#                         elif token[1] == 'OR':
#                             result = left.union(right)
#                         else:
#                             result = set()
#                         stack.append(result)
        
#         return list(stack[0]) if stack else set()
    
#     def phrase_search(self, phrase):
#         """Find exact phrase matches"""
#         phrase_lower = phrase.lower()
#         matching_docs = set()
#         for doc_id, doc in self.indexer.documents.items():
#             if phrase_lower in doc['content'].lower():
#                 matching_docs.add(doc_id)
#         return matching_docs
    
#     def fuzzy_search(self, term, max_distance=2):
#         """Fuzzy search - matches words with typos"""
#         term = term.lower()
#         matches = set()
        
#         for word in self.indexer.inverted_index.keys():
#             if abs(len(word) - len(term)) <= max_distance:
#                 distance = self.levenshtein_distance(term, word)
#                 if distance <= max_distance:
#                     matches.update(self.indexer.inverted_index[word].keys())
#         return matches
    
#     def levenshtein_distance(self, s1, s2):
#         """Calculate edit distance"""
#         if len(s1) < len(s2):
#             return self.levenshtein_distance(s2, s1)
#         if len(s2) == 0:
#             return len(s1)
        
#         previous_row = list(range(len(s2) + 1))
#         for i, c1 in enumerate(s1):
#             current_row = [i + 1]
#             for j, c2 in enumerate(s2):
#                 insertions = previous_row[j + 1] + 1
#                 deletions = current_row[j] + 1
#                 substitutions = previous_row[j] + (c1 != c2)
#                 current_row.append(min(insertions, deletions, substitutions))
#             previous_row = current_row
#         return previous_row[-1]
    
#     def wildcard_search(self, pattern):
#         """Wildcard: * (multiple chars) and ? (single char)"""
#         pattern = pattern.lower()
#         matches = set()
        
#         # Convert to regex
#         regex_pattern = re.escape(pattern).replace(r'\*', '.*').replace(r'\?', '.')
        
#         if pattern.startswith('*'):
#             regex = re.compile(f'.*{regex_pattern[1:]}$')
#         elif pattern.endswith('*'):
#             regex = re.compile(f'^{regex_pattern[:-2]}.*$')
#         else:
#             regex = re.compile(f'^{regex_pattern}$')
        
#         for word in self.indexer.inverted_index.keys():
#             if regex.match(word):
#                 matches.update(self.indexer.inverted_index[word].keys())
        
#         return matches
    
#     def apply_filters(self, results, date_from, date_to, file_types):
#         """Apply date and file type filters"""
#         if not results:
#             return results
        
#         filtered = []
#         for doc_id in results:
#             doc = self.indexer.documents[doc_id]
            
#             if date_from or date_to:
#                 doc_date = datetime.fromtimestamp(doc['timestamp'])
#                 if date_from and doc_date < date_from:
#                     continue
#                 if date_to and doc_date > date_to:
#                     continue
            
#             if file_types and doc['type'] not in file_types:
#                 continue
            
#             filtered.append(doc_id)
        
#         return filtered
    
#     def score_results(self, results):
#         """Score by term frequency"""
#         scored = []
#         for doc_id in results:
#             score = 0
#             for term, posting in self.indexer.inverted_index.items():
#                 if doc_id in posting:
#                     score += len(posting[doc_id])
#             scored.append((doc_id, score))
#         scored.sort(key=lambda x: x[1], reverse=True)
#         return scored
    
#     def get_snippet(self, doc_id, query_terms, max_length=150):
#         """Get highlighted snippet"""
#         content = self.indexer.documents[doc_id]['content']
#         words = content.split()
        
#         if not words:
#             return ""
        
#         best_pos = 0
#         max_matches = 0
        
#         for i, word in enumerate(words):
#             matches = 0
#             for term in query_terms:
#                 term_clean = term.strip('"').lower()
#                 if term_clean in word.lower():
#                     matches += 1
#             if matches > max_matches:
#                 max_matches = matches
#                 best_pos = i
        
#         start = max(0, best_pos - 25)
#         end = min(len(words), best_pos + 25)
#         snippet = ' '.join(words[start:end])
        
#         for term in query_terms:
#             term_clean = term.strip('"').lower()
#             snippet = re.sub(f'({re.escape(term_clean)})', r'<mark>\1</mark>', snippet, flags=re.IGNORECASE)
        
#         if len(snippet) > max_length:
#             snippet = snippet[:max_length] + "..."
        
#         return snippet
    
#     def did_you_mean(self, query):
#         """Suggest correction for typos"""
#         words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
#         all_words = list(self.indexer.inverted_index.keys())
        
#         suggestions = []
#         for word in words:
#             matches = get_close_matches(word, all_words, n=1, cutoff=0.7)
#             if matches:
#                 suggestions.append(matches[0])
#             else:
#                 suggestions.append(word)
        
#         if suggestions != words:
#             return ' '.join(suggestions)
#         return None











# # search.py - Complete working search engine with proper highlighting
# import re
# from datetime import datetime
# from difflib import get_close_matches

# class SearchEngine:
#     def __init__(self, indexer):
#         self.indexer = indexer
#         self.current_results = []
    
#     def search(self, query, date_from=None, date_to=None, file_types=None):
#         """Main search function - supports ALL query types"""
#         if not self.indexer.inverted_index:
#             print("❌ No index loaded! Build index first.")
#             return []
        
#         try:
#             parsed = self.parse_query(query)
#             if not parsed:
#                 return []
            
#             results = self.execute_query(parsed)
#             results = self.apply_filters(results, date_from, date_to, file_types)
#             results = self.score_results(results)
#             self.current_results = results
#             return results
#         except Exception as e:
#             print(f"Search error: {e}")
#             return []
    
#     def parse_query(self, query):
#         """Parse ALL query types: boolean, phrase, fuzzy, wildcard with parentheses"""
#         query = query.strip()
        
#         # Step 1: Replace phrase queries "exact phrase" with placeholders
#         phrases = re.findall(r'"([^"]+)"', query)
#         phrase_map = {}
#         for i, phrase in enumerate(phrases):
#             placeholder = f"__PHRASE_{i}__"
#             phrase_map[placeholder] = phrase
#             query = query.replace(f'"{phrase}"', placeholder)
        
#         # Step 2: Replace fuzzy queries word~ or word~2
#         def replace_fuzzy(match):
#             word = match.group(1)
#             dist = match.group(2) if match.group(2) else '2'
#             return f'__FUZZY_{word}_{dist}__'
        
#         query = re.sub(r'(\w+)~(\d*)?', replace_fuzzy, query)
        
#         # Step 3: Tokenize (split by spaces, preserve parentheses)
#         tokens = []
#         current = ""
#         for char in query:
#             if char == ' ' and current:
#                 tokens.append(current)
#                 current = ""
#             elif char == '(' or char == ')':
#                 if current:
#                     tokens.append(current)
#                     current = ""
#                 tokens.append(char)
#             else:
#                 current += char
#         if current:
#             tokens.append(current)
        
#         # Step 4: Process each token
#         parsed = []
#         for token in tokens:
#             if token == '(':
#                 parsed.append(('LPAREN', None))
#             elif token == ')':
#                 parsed.append(('RPAREN', None))
#             elif token.upper() == 'AND':
#                 parsed.append(('OP', 'AND'))
#             elif token.upper() == 'OR':
#                 parsed.append(('OP', 'OR'))
#             elif token.upper() == 'NOT':
#                 parsed.append(('OP', 'NOT'))
#             elif token.startswith('__PHRASE_'):
#                 phrase = phrase_map.get(token, '')
#                 parsed.append(('PHRASE', phrase))
#             elif token.startswith('__FUZZY_'):
#                 parts = token.replace('__FUZZY_', '').replace('__', '').split('_')
#                 word = parts[0]
#                 dist = int(parts[1]) if len(parts) > 1 else 2
#                 parsed.append(('FUZZY', word, dist))
#             elif '*' in token or '?' in token:
#                 parsed.append(('WILDCARD', token))
#             else:
#                 parsed.append(('TERM', token.lower()))
        
#         # Step 5: Convert to postfix (RPN) for proper operator precedence
#         return self.to_postfix(parsed)
    
#     def to_postfix(self, tokens):
#         """Convert infix to postfix (Shunting Yard algorithm)"""
#         output = []
#         stack = []
#         precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
        
#         for token in tokens:
#             if token[0] in ['TERM', 'PHRASE', 'FUZZY', 'WILDCARD']:
#                 output.append(token)
#             elif token[0] == 'OP':
#                 while (stack and stack[-1][0] == 'OP' and 
#                        precedence.get(stack[-1][1], 0) >= precedence.get(token[1], 0)):
#                     output.append(stack.pop())
#                 stack.append(token)
#             elif token[0] == 'LPAREN':
#                 stack.append(token)
#             elif token[0] == 'RPAREN':
#                 while stack and stack[-1][0] != 'LPAREN':
#                     output.append(stack.pop())
#                 if stack and stack[-1][0] == 'LPAREN':
#                     stack.pop()
        
#         while stack:
#             output.append(stack.pop())
        
#         return output
    
#     def execute_query(self, parsed):
#         """Execute postfix query using stack"""
#         if not parsed:
#             return set()
        
#         stack = []
        
#         for token in parsed:
#             if token[0] == 'TERM':
#                 docs = set(self.indexer.inverted_index.get(token[1], {}).keys())
#                 stack.append(docs)
#             elif token[0] == 'PHRASE':
#                 docs = self.phrase_search(token[1])
#                 stack.append(docs)
#             elif token[0] == 'FUZZY':
#                 docs = self.fuzzy_search(token[1], token[2])
#                 stack.append(docs)
#             elif token[0] == 'WILDCARD':
#                 docs = self.wildcard_search(token[1])
#                 stack.append(docs)
#             elif token[0] == 'OP':
#                 if token[1] == 'NOT':
#                     if len(stack) >= 1:
#                         right = stack.pop()
#                         all_docs = set(self.indexer.documents.keys())
#                         result = all_docs - right
#                         stack.append(result)
#                 else:
#                     if len(stack) >= 2:
#                         right = stack.pop()
#                         left = stack.pop()
#                         if token[1] == 'AND':
#                             result = left.intersection(right)
#                         elif token[1] == 'OR':
#                             result = left.union(right)
#                         else:
#                             result = set()
#                         stack.append(result)
        
#         return list(stack[0]) if stack else set()
    
#     def phrase_search(self, phrase):
#         """Find exact phrase matches"""
#         phrase_lower = phrase.lower()
#         matching_docs = set()
#         for doc_id, doc in self.indexer.documents.items():
#             if phrase_lower in doc['content'].lower():
#                 matching_docs.add(doc_id)
#         return matching_docs
    
#     def fuzzy_search(self, term, max_distance=2):
#         """Fuzzy search - matches words with typos"""
#         term = term.lower()
#         matches = set()
        
#         for word in self.indexer.inverted_index.keys():
#             if abs(len(word) - len(term)) <= max_distance:
#                 distance = self.levenshtein_distance(term, word)
#                 if distance <= max_distance:
#                     matches.update(self.indexer.inverted_index[word].keys())
#         return matches
    
#     def levenshtein_distance(self, s1, s2):
#         """Calculate edit distance"""
#         if len(s1) < len(s2):
#             return self.levenshtein_distance(s2, s1)
#         if len(s2) == 0:
#             return len(s1)
        
#         previous_row = list(range(len(s2) + 1))
#         for i, c1 in enumerate(s1):
#             current_row = [i + 1]
#             for j, c2 in enumerate(s2):
#                 insertions = previous_row[j + 1] + 1
#                 deletions = current_row[j] + 1
#                 substitutions = previous_row[j] + (c1 != c2)
#                 current_row.append(min(insertions, deletions, substitutions))
#             previous_row = current_row
#         return previous_row[-1]
    
#     def wildcard_search(self, pattern):
#         """Wildcard: * (multiple chars) and ? (single char)"""
#         pattern = pattern.lower()
#         matches = set()
        
#         # Convert to regex
#         regex_pattern = re.escape(pattern).replace(r'\*', '.*').replace(r'\?', '.')
        
#         if pattern.startswith('*'):
#             regex = re.compile(f'.*{regex_pattern[1:]}$')
#         elif pattern.endswith('*'):
#             regex = re.compile(f'^{regex_pattern[:-2]}.*$')
#         else:
#             regex = re.compile(f'^{regex_pattern}$')
        
#         for word in self.indexer.inverted_index.keys():
#             if regex.match(word):
#                 matches.update(self.indexer.inverted_index[word].keys())
        
#         return matches
    
#     def apply_filters(self, results, date_from, date_to, file_types):
#         """Apply date and file type filters"""
#         if not results:
#             return results
        
#         filtered = []
#         for doc_id in results:
#             doc = self.indexer.documents[doc_id]
            
#             if date_from or date_to:
#                 doc_date = datetime.fromtimestamp(doc['timestamp'])
#                 if date_from and doc_date < date_from:
#                     continue
#                 if date_to and doc_date > date_to:
#                     continue
            
#             if file_types and doc['type'] not in file_types:
#                 continue
            
#             filtered.append(doc_id)
        
#         return filtered
    
#     def score_results(self, results):
#         """Score by term frequency"""
#         scored = []
#         for doc_id in results:
#             score = 0
#             for term, posting in self.indexer.inverted_index.items():
#                 if doc_id in posting:
#                     score += len(posting[doc_id])
#             scored.append((doc_id, score))
#         scored.sort(key=lambda x: x[1], reverse=True)
#         return scored
    
#     def get_snippet(self, doc_id, query_terms, max_length=150):
#         """Get highlighted snippet - ignores operators like AND, OR, NOT"""
#         content = self.indexer.documents[doc_id]['content']
#         words = content.split()
        
#         if not words:
#             return ""
        
#         # Operators to ignore in highlighting
#         operators = {'and', 'or', 'not'}
        
#         # Extract actual search terms (exclude operators)
#         clean_terms = []
#         for term in query_terms:
#             term_lower = term.lower().strip('"')
#             if term_lower not in operators and len(term_lower) > 1:
#                 clean_terms.append(term_lower)
        
#         # If no search terms, return beginning of content
#         if not clean_terms:
#             snippet = ' '.join(words[:50])
#             if len(snippet) > max_length:
#                 snippet = snippet[:max_length] + "..."
#             return snippet
        
#         # Find best snippet position (where most terms appear)
#         best_pos = 0
#         max_matches = 0
        
#         for i, word in enumerate(words):
#             matches = 0
#             for term in clean_terms:
#                 if term in word.lower():
#                     matches += 1
#             if matches > max_matches:
#                 max_matches = matches
#                 best_pos = i
        
#         # Extract snippet around best position
#         start = max(0, best_pos - 25)
#         end = min(len(words), best_pos + 25)
#         snippet = ' '.join(words[start:end])
        
#         # Highlight ONLY the clean terms (not operators)
#         for term in clean_terms:
#             snippet = re.sub(f'({re.escape(term)})', r'<mark>\1</mark>', snippet, flags=re.IGNORECASE)
        
#         # Truncate if too long
#         if len(snippet) > max_length:
#             snippet = snippet[:max_length] + "..."
        
#         return snippet
    
#     def did_you_mean(self, query):
#         """Suggest correction for typos"""
#         # Extract words from query (ignore operators)
#         operators = {'and', 'or', 'not'}
#         words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
#         words = [w for w in words if w not in operators]
        
#         all_words = list(self.indexer.inverted_index.keys())
        
#         suggestions = []
#         for word in words:
#             matches = get_close_matches(word, all_words, n=1, cutoff=0.7)
#             if matches:
#                 suggestions.append(matches[0])
#             else:
#                 suggestions.append(word)
        
#         if suggestions != words:
#             # Rebuild query with suggestions
#             result = query.lower()
#             for original, suggested in zip(words, suggestions):
#                 if original != suggested:
#                     result = result.replace(original, suggested)
#             return result
#         return None
    
#     def extract_search_terms(self, query):
#         """Extract only the actual search terms (no operators)"""
#         operators = {'and', 'or', 'not'}
#         words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
#         return [w for w in words if w not in operators]

















# search.py - Complete working search engine with FULL highlighting
import re
from datetime import datetime
from difflib import get_close_matches

class SearchEngine:
    def __init__(self, indexer):
        self.indexer = indexer
        self.current_results = []
    
    def search(self, query, date_from=None, date_to=None, file_types=None):
        """Main search function - supports ALL query types"""
        if not self.indexer.inverted_index:
            print("❌ No index loaded! Build index first.")
            return []
        
        try:
            # Store original query for highlighting
            self.original_query = query
            
            parsed = self.parse_query(query)
            if not parsed:
                return []
            
            results = self.execute_query(parsed)
            results = self.apply_filters(results, date_from, date_to, file_types)
            results = self.score_results(results)
            self.current_results = results
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def parse_query(self, query):
        """Parse ALL query types: boolean, phrase, fuzzy, wildcard with parentheses"""
        query = query.strip()
        
        # Store for highlighting
        self.original_query = query
        
        # Step 1: Replace phrase queries "exact phrase" with placeholders
        phrases = re.findall(r'"([^"]+)"', query)
        self.phrase_map = {}
        for i, phrase in enumerate(phrases):
            placeholder = f"__PHRASE_{i}__"
            self.phrase_map[placeholder] = phrase
            query = query.replace(f'"{phrase}"', placeholder)
        
        # Step 2: Replace fuzzy queries word~ or word~2
        self.fuzzy_map = {}
        def replace_fuzzy(match):
            word = match.group(1)
            dist = match.group(2) if match.group(2) else '2'
            placeholder = f"__FUZZY_{len(self.fuzzy_map)}__"
            self.fuzzy_map[placeholder] = {'word': word, 'dist': int(dist)}
            return placeholder
        
        query = re.sub(r'(\w+)~(\d*)?', replace_fuzzy, query)
        
        # Step 3: Replace wildcard queries
        self.wildcard_map = {}
        def replace_wildcard(match):
            pattern = match.group(0)
            placeholder = f"__WILDCARD_{len(self.wildcard_map)}__"
            self.wildcard_map[placeholder] = pattern
            return placeholder
        
        query = re.sub(r'[\w\*\+\?]+[\*\?]+[\w\*\+\?]*', replace_wildcard, query)
        
        # Step 4: Tokenize (split by spaces, preserve parentheses)
        tokens = []
        current = ""
        for char in query:
            if char == ' ' and current:
                tokens.append(current)
                current = ""
            elif char == '(' or char == ')':
                if current:
                    tokens.append(current)
                    current = ""
                tokens.append(char)
            else:
                current += char
        if current:
            tokens.append(current)
        
        # Step 5: Process each token
        parsed = []
        self.search_terms = []  # Store for highlighting
        self.wildcard_patterns = []
        self.fuzzy_words = []
        
        for token in tokens:
            if token == '(':
                parsed.append(('LPAREN', None))
            elif token == ')':
                parsed.append(('RPAREN', None))
            elif token.upper() == 'AND':
                parsed.append(('OP', 'AND'))
            elif token.upper() == 'OR':
                parsed.append(('OP', 'OR'))
            elif token.upper() == 'NOT':
                parsed.append(('OP', 'NOT'))
            elif token.startswith('__PHRASE_'):
                phrase = self.phrase_map.get(token, '')
                parsed.append(('PHRASE', phrase))
                self.search_terms.append(phrase)
            elif token.startswith('__FUZZY_'):
                fuzzy_data = self.fuzzy_map.get(token, {})
                word = fuzzy_data.get('word', '')
                dist = fuzzy_data.get('dist', 2)
                parsed.append(('FUZZY', word, dist))
                self.fuzzy_words.append({'original': f"{word}~{dist}", 'word': word})
                self.search_terms.append(word)
            elif token.startswith('__WILDCARD_'):
                pattern = self.wildcard_map.get(token, '')
                parsed.append(('WILDCARD', pattern))
                self.wildcard_patterns.append(pattern)
                # For highlighting, use pattern without wildcards
                clean_pattern = re.sub(r'[\*\?]', '', pattern)
                if clean_pattern:
                    self.search_terms.append(clean_pattern)
            else:
                parsed.append(('TERM', token.lower()))
                self.search_terms.append(token.lower())
        
        # Step 6: Convert to postfix (RPN) for proper operator precedence
        return self.to_postfix(parsed)
    
    def to_postfix(self, tokens):
        """Convert infix to postfix (Shunting Yard algorithm)"""
        output = []
        stack = []
        precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
        
        for token in tokens:
            if token[0] in ['TERM', 'PHRASE', 'FUZZY', 'WILDCARD']:
                output.append(token)
            elif token[0] == 'OP':
                while (stack and stack[-1][0] == 'OP' and 
                       precedence.get(stack[-1][1], 0) >= precedence.get(token[1], 0)):
                    output.append(stack.pop())
                stack.append(token)
            elif token[0] == 'LPAREN':
                stack.append(token)
            elif token[0] == 'RPAREN':
                while stack and stack[-1][0] != 'LPAREN':
                    output.append(stack.pop())
                if stack and stack[-1][0] == 'LPAREN':
                    stack.pop()
        
        while stack:
            output.append(stack.pop())
        
        return output
    
    def execute_query(self, parsed):
        """Execute postfix query using stack"""
        if not parsed:
            return set()
        
        stack = []
        
        for token in parsed:
            if token[0] == 'TERM':
                docs = set(self.indexer.inverted_index.get(token[1], {}).keys())
                stack.append(docs)
            elif token[0] == 'PHRASE':
                docs = self.phrase_search(token[1])
                stack.append(docs)
            elif token[0] == 'FUZZY':
                docs = self.fuzzy_search(token[1], token[2])
                stack.append(docs)
            elif token[0] == 'WILDCARD':
                docs = self.wildcard_search(token[1])
                stack.append(docs)
            elif token[0] == 'OP':
                if token[1] == 'NOT':
                    if len(stack) >= 1:
                        right = stack.pop()
                        all_docs = set(self.indexer.documents.keys())
                        result = all_docs - right
                        stack.append(result)
                else:
                    if len(stack) >= 2:
                        right = stack.pop()
                        left = stack.pop()
                        if token[1] == 'AND':
                            result = left.intersection(right)
                        elif token[1] == 'OR':
                            result = left.union(right)
                        else:
                            result = set()
                        stack.append(result)
        
        return list(stack[0]) if stack else set()
    
    def phrase_search(self, phrase):
        """Find exact phrase matches"""
        phrase_lower = phrase.lower()
        matching_docs = set()
        for doc_id, doc in self.indexer.documents.items():
            if phrase_lower in doc['content'].lower():
                matching_docs.add(doc_id)
        return matching_docs
    
    def fuzzy_search(self, term, max_distance=2):
        """Fuzzy search - matches words with typos"""
        term = term.lower()
        matches = set()
        
        for word in self.indexer.inverted_index.keys():
            if abs(len(word) - len(term)) <= max_distance:
                distance = self.levenshtein_distance(term, word)
                if distance <= max_distance:
                    matches.update(self.indexer.inverted_index[word].keys())
        return matches
    
    def levenshtein_distance(self, s1, s2):
        """Calculate edit distance"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]
    
    def wildcard_search(self, pattern):
        """Wildcard: * (multiple chars) and ? (single char)"""
        pattern = pattern.lower()
        matches = set()
        
        # Convert to regex
        regex_pattern = re.escape(pattern).replace(r'\*', '.*').replace(r'\?', '.')
        
        if pattern.startswith('*'):
            regex = re.compile(f'.*{regex_pattern[1:]}$')
        elif pattern.endswith('*'):
            regex = re.compile(f'^{regex_pattern[:-2]}.*$')
        else:
            regex = re.compile(f'^{regex_pattern}$')
        
        for word in self.indexer.inverted_index.keys():
            if regex.match(word):
                matches.update(self.indexer.inverted_index[word].keys())
        
        return matches
    
    def apply_filters(self, results, date_from, date_to, file_types):
        """Apply date and file type filters"""
        if not results:
            return results
        
        filtered = []
        for doc_id in results:
            doc = self.indexer.documents[doc_id]
            
            if date_from or date_to:
                doc_date = datetime.fromtimestamp(doc['timestamp'])
                if date_from and doc_date < date_from:
                    continue
                if date_to and doc_date > date_to:
                    continue
            
            if file_types and doc['type'] not in file_types:
                continue
            
            filtered.append(doc_id)
        
        return filtered
    
    def score_results(self, results):
        """Score by term frequency"""
        scored = []
        for doc_id in results:
            score = 0
            for term, posting in self.indexer.inverted_index.items():
                if doc_id in posting:
                    score += len(posting[doc_id])
            scored.append((doc_id, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def get_snippet(self, doc_id, query_terms, max_length=150):
        """Get highlighted snippet - highlights ALL search terms (phrases, fuzzy, wildcard)"""
        content = self.indexer.documents[doc_id]['content']
        
        if not content:
            return ""
        
        # Operators to ignore in highlighting
        operators = {'and', 'or', 'not'}
        
        # Build list of terms to highlight
        highlight_terms = []
        
        # Add regular terms
        for term in query_terms:
            term_lower = term.lower().strip('"')
            if term_lower not in operators and len(term_lower) > 1:
                highlight_terms.append(term_lower)
        
        # Add phrase terms (from parsed query)
        if hasattr(self, 'phrase_map'):
            for phrase in self.phrase_map.values():
                if phrase:
                    highlight_terms.append(phrase.lower())
        
        # Add fuzzy words
        if hasattr(self, 'fuzzy_words'):
            for fuzzy in self.fuzzy_words:
                if fuzzy['word']:
                    highlight_terms.append(fuzzy['word'])
        
        # Add wildcard patterns (clean them)
        if hasattr(self, 'wildcard_patterns'):
            for pattern in self.wildcard_patterns:
                clean_pattern = re.sub(r'[\*\?]', '', pattern)
                if clean_pattern and len(clean_pattern) > 1:
                    highlight_terms.append(clean_pattern)
        
        # Remove duplicates
        highlight_terms = list(set(highlight_terms))
        
        # If no highlight terms, return beginning of content
        if not highlight_terms:
            words = content.split()
            snippet = ' '.join(words[:50])
            if len(snippet) > max_length:
                snippet = snippet[:max_length] + "..."
            return snippet
        
        # Split content into words
        words = content.split()
        if not words:
            return ""
        
        # Find best snippet position (where most highlight terms appear)
        best_pos = 0
        max_matches = 0
        
        for i, word in enumerate(words):
            matches = 0
            word_lower = word.lower()
            for term in highlight_terms:
                if term.lower() in word_lower:
                    matches += 1
                # Also check if term is substring of word (for wildcard)
                if len(term) > 2 and term.lower() in word_lower:
                    matches += 1
            if matches > max_matches:
                max_matches = matches
                best_pos = i
        
        # Extract snippet around best position
        start = max(0, best_pos - 25)
        end = min(len(words), best_pos + 25)
        snippet = ' '.join(words[start:end])
        
        # Highlight ALL matching terms
        for term in highlight_terms:
            # Build pattern for exact word or part of word
            pattern = re.compile(f'({re.escape(term)})', re.IGNORECASE)
            snippet = pattern.sub(r'<mark>\1</mark>', snippet)
        
        # Truncate if too long
        if len(snippet) > max_length:
            snippet = snippet[:max_length] + "..."
        
        return snippet
    
    def get_all_search_terms(self, query):
        """Extract ALL search terms including phrases, fuzzy, wildcard"""
        self.parse_query(query)  # This populates the term lists
        all_terms = []
        
        # Regular terms
        if hasattr(self, 'search_terms'):
            all_terms.extend(self.search_terms)
        
        # Phrases
        if hasattr(self, 'phrase_map'):
            for phrase in self.phrase_map.values():
                if phrase:
                    all_terms.append(phrase)
        
        # Fuzzy words
        if hasattr(self, 'fuzzy_words'):
            for fuzzy in self.fuzzy_words:
                if fuzzy['word']:
                    all_terms.append(fuzzy['word'])
        
        # Wildcard patterns (cleaned)
        if hasattr(self, 'wildcard_patterns'):
            for pattern in self.wildcard_patterns:
                clean = re.sub(r'[\*\?]', '', pattern)
                if clean:
                    all_terms.append(clean)
        
        return list(set(all_terms))
    
    def did_you_mean(self, query):
        """Suggest correction for typos - works with any query type"""
        # Parse to get terms
        self.parse_query(query)
        
        # Get all search terms
        search_terms = self.get_all_search_terms(query)
        
        all_index_words = list(self.indexer.inverted_index.keys())
        
        suggestions = []
        for term in search_terms:
            if len(term) < 3:
                suggestions.append(term)
                continue
            
            # For phrases, suggest each word
            if ' ' in term:
                words = term.split()
                for w in words:
                    matches = get_close_matches(w, all_index_words, n=1, cutoff=0.7)
                    if matches and matches[0] != w:
                        term = term.replace(w, matches[0])
                suggestions.append(term)
            else:
                matches = get_close_matches(term, all_index_words, n=1, cutoff=0.7)
                if matches and matches[0] != term:
                    suggestions.append(matches[0])
                else:
                    suggestions.append(term)
        
        # Reconstruct query preserving structure
        if suggestions != search_terms:
            result = query
            for original, suggested in zip(search_terms, suggestions):
                if original != suggested:
                    result = result.replace(original, suggested)
            return result
        return None
    
    def extract_search_terms(self, query):
        """Extract only the actual search terms (no operators)"""
        operators = {'and', 'or', 'not'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        return [w for w in words if w not in operators]