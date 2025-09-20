"""
Demand integration API for laser equipment intelligence platform
"""

import json
import time
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from laser_intelligence.utils.brand_mapping import BrandMapper


class DemandAPI:
    """API for demand integration and management"""
    
    def __init__(self, database_url: str):
        self.app = Flask(__name__)
        CORS(self.app)
        self.database_url = database_url
        self.brand_mapper = BrandMapper()
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up API routes"""
        
        @self.app.route('/api/v1/demand/update', methods=['POST'])
        def update_demand():
            """Update demand items via API"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                demand_items = data.get('demand_items', [])
                update_type = data.get('update_type', 'append')
                
                if not demand_items:
                    return jsonify({'error': 'No demand items provided'}), 400
                
                # Validate and process demand items
                processed_items = self._process_demand_items(demand_items)
                
                # Update database
                result = self._update_demand_database(processed_items, update_type)
                
                return jsonify({
                    'success': True,
                    'message': f'Updated {len(processed_items)} demand items',
                    'items_processed': len(processed_items),
                    'update_type': update_type,
                    'timestamp': time.time()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/demand/list', methods=['GET'])
        def list_demand():
            """List current demand items"""
            try:
                active_only = request.args.get('active_only', 'true').lower() == 'true'
                brand_filter = request.args.get('brand')
                urgency_filter = request.args.get('urgency')
                
                demand_items = self._get_demand_items(
                    active_only=active_only,
                    brand_filter=brand_filter,
                    urgency_filter=urgency_filter
                )
                
                return jsonify({
                    'success': True,
                    'demand_items': demand_items,
                    'count': len(demand_items),
                    'timestamp': time.time()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/demand/delete/<item_id>', methods=['DELETE'])
        def delete_demand_item(item_id):
            """Delete a specific demand item"""
            try:
                success = self._delete_demand_item(item_id)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Deleted demand item {item_id}',
                        'timestamp': time.time()
                    })
                else:
                    return jsonify({'error': 'Demand item not found'}), 404
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/demand/matches', methods=['GET'])
        def get_demand_matches():
            """Get listings that match current demand"""
            try:
                brand_filter = request.args.get('brand')
                urgency_filter = request.args.get('urgency')
                min_score = float(request.args.get('min_score', 50))
                
                matches = self._get_demand_matches(
                    brand_filter=brand_filter,
                    urgency_filter=urgency_filter,
                    min_score=min_score
                )
                
                return jsonify({
                    'success': True,
                    'matches': matches,
                    'count': len(matches),
                    'timestamp': time.time()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/demand/upload', methods=['POST'])
        def upload_demand_csv():
            """Upload demand items via CSV file"""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                if not file.filename.endswith('.csv'):
                    return jsonify({'error': 'File must be a CSV'}), 400
                
                # Parse CSV
                csv_content = file.read().decode('utf-8')
                demand_items = self._parse_csv_demand(csv_content)
                
                # Update database
                result = self._update_demand_database(demand_items, 'append')
                
                return jsonify({
                    'success': True,
                    'message': f'Uploaded {len(demand_items)} demand items from CSV',
                    'items_processed': len(demand_items),
                    'timestamp': time.time()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            try:
                # Test database connection
                conn = psycopg2.connect(self.database_url)
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
                conn.close()
                
                return jsonify({
                    'status': 'healthy',
                    'timestamp': time.time(),
                    'database': 'connected'
                })
                
            except Exception as e:
                return jsonify({
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': time.time()
                }), 500
    
    def _process_demand_items(self, demand_items: List[Dict]) -> List[Dict]:
        """Process and validate demand items"""
        processed_items = []
        
        for item in demand_items:
            try:
                # Validate required fields
                if not item.get('brand') or not item.get('model'):
                    continue
                
                # Normalize brand and model
                brand = self.brand_mapper.normalize_brand(item['brand'])
                model = self.brand_mapper.normalize_model(item['model'], item['brand'])
                
                processed_item = {
                    'brand': brand,
                    'model': model,
                    'condition': item.get('condition', 'any'),
                    'urgency': item.get('urgency', 'medium'),
                    'quantity_needed': int(item.get('quantity_needed', 1)),
                    'max_price': float(item.get('max_price', 0)) if item.get('max_price') else None,
                    'buyer_contact': item.get('buyer_contact', ''),
                    'notes': item.get('notes', ''),
                    'expires_at': item.get('expires_at'),
                    'created_at': time.time()
                }
                
                processed_items.append(processed_item)
                
            except (ValueError, TypeError) as e:
                print(f'Error processing demand item: {e}')
                continue
        
        return processed_items
    
    def _update_demand_database(self, demand_items: List[Dict], update_type: str) -> bool:
        """Update demand items in database"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            if update_type == 'replace':
                # Clear existing demand items
                cursor.execute('DELETE FROM demand_items')
            
            # Insert new demand items
            for item in demand_items:
                cursor.execute("""
                    INSERT INTO demand_items 
                    (brand, model, condition, urgency, quantity_needed, max_price, 
                     buyer_contact, notes, expires_at, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    item['brand'],
                    item['model'],
                    item['condition'],
                    item['urgency'],
                    item['quantity_needed'],
                    item['max_price'],
                    item['buyer_contact'],
                    item['notes'],
                    item['expires_at'],
                    item['created_at']
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f'Error updating demand database: {e}')
            return False
    
    def _get_demand_items(self, active_only: bool = True, 
                         brand_filter: Optional[str] = None,
                         urgency_filter: Optional[str] = None) -> List[Dict]:
        """Get demand items from database"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = 'SELECT * FROM demand_items WHERE 1=1'
            params = []
            
            if active_only:
                query += ' AND (expires_at IS NULL OR expires_at > %s)'
                params.append(time.time())
            
            if brand_filter:
                query += ' AND brand ILIKE %s'
                params.append(f'%{brand_filter}%')
            
            if urgency_filter:
                query += ' AND urgency = %s'
                params.append(urgency_filter)
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f'Error getting demand items: {e}')
            return []
    
    def _delete_demand_item(self, item_id: str) -> bool:
        """Delete a specific demand item"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM demand_items WHERE id = %s', (item_id,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return deleted_count > 0
            
        except Exception as e:
            print(f'Error deleting demand item: {e}')
            return False
    
    def _get_demand_matches(self, brand_filter: Optional[str] = None,
                           urgency_filter: Optional[str] = None,
                           min_score: float = 50) -> List[Dict]:
        """Get listings that match current demand"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get active demand items
            demand_query = 'SELECT * FROM demand_items WHERE (expires_at IS NULL OR expires_at > %s)'
            demand_params = [time.time()]
            
            if brand_filter:
                demand_query += ' AND brand ILIKE %s'
                demand_params.append(f'%{brand_filter}%')
            
            if urgency_filter:
                demand_query += ' AND urgency = %s'
                demand_params.append(urgency_filter)
            
            cursor.execute(demand_query, demand_params)
            demand_items = cursor.fetchall()
            
            matches = []
            
            for demand_item in demand_items:
                # Find matching listings
                listing_query = """
                    SELECT l.*, s.name as source_name
                    FROM listings l
                    JOIN sources s ON l.source_id = s.id
                    WHERE l.brand ILIKE %s 
                    AND l.model ILIKE %s
                    AND l.score_overall >= %s
                    AND l.pipeline_status = 'new'
                    ORDER BY l.score_overall DESC
                    LIMIT 10
                """
                
                listing_params = [
                    f'%{demand_item["brand"]}%',
                    f'%{demand_item["model"]}%',
                    min_score
                ]
                
                cursor.execute(listing_query, listing_params)
                listings = cursor.fetchall()
                
                for listing in listings:
                    match = {
                        'demand_item': dict(demand_item),
                        'listing': dict(listing),
                        'match_score': self._calculate_match_score(demand_item, listing),
                        'timestamp': time.time()
                    }
                    matches.append(match)
            
            cursor.close()
            conn.close()
            
            return matches
            
        except Exception as e:
            print(f'Error getting demand matches: {e}')
            return []
    
    def _calculate_match_score(self, demand_item: Dict, listing: Dict) -> float:
        """Calculate match score between demand item and listing"""
        score = 0.0
        
        # Brand match
        if demand_item['brand'].lower() == listing['brand'].lower():
            score += 40
        elif demand_item['brand'].lower() in listing['brand'].lower():
            score += 30
        
        # Model match
        if demand_item['model'].lower() == listing['model'].lower():
            score += 30
        elif demand_item['model'].lower() in listing['model'].lower():
            score += 20
        
        # Condition match
        if demand_item['condition'] == 'any' or demand_item['condition'] == listing['condition']:
            score += 10
        
        # Price match
        if demand_item['max_price'] and listing['asking_price']:
            if listing['asking_price'] <= demand_item['max_price']:
                score += 20
        
        # Urgency bonus
        if demand_item['urgency'] == 'high':
            score += 10
        
        return min(100, score)
    
    def _parse_csv_demand(self, csv_content: str) -> List[Dict]:
        """Parse CSV content into demand items"""
        import csv
        import io
        
        demand_items = []
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        for row in csv_reader:
            try:
                demand_item = {
                    'brand': row.get('brand', '').strip(),
                    'model': row.get('model', '').strip(),
                    'condition': row.get('condition', 'any').strip(),
                    'urgency': row.get('urgency', 'medium').strip(),
                    'quantity_needed': int(row.get('quantity_needed', 1)),
                    'max_price': float(row.get('max_price', 0)) if row.get('max_price') else None,
                    'buyer_contact': row.get('buyer_contact', '').strip(),
                    'notes': row.get('notes', '').strip(),
                    'expires_at': row.get('expires_at')
                }
                
                demand_items.append(demand_item)
                
            except (ValueError, TypeError) as e:
                print(f'Error parsing CSV row: {e}')
                continue
        
        return demand_items
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the API server"""
        self.app.run(host=host, port=port, debug=debug)


def create_app(database_url: str) -> Flask:
    """Create Flask app for demand API"""
    api = DemandAPI(database_url)
    return api.app


if __name__ == '__main__':
    import os
    database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/laser_intelligence')
    api = DemandAPI(database_url)
    api.run(debug=True)
