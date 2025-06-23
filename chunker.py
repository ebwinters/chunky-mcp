import json
import hashlib
import tempfile
import os

class ResponseChunker:
    def __init__(self):
        self.temp_files = {}
        self.MAX_RESPONSE_SIZE = 50000
        self.MAX_CHUNK_SIZE = 30000

    def save_large_response(self, response_data, tool_name, params_hash):
        """Save large response to temporary file and return metadata"""
        response_json = json.dumps(response_data, indent=2)
        
        # Create unique filename
        file_id = f"{tool_name}_{params_hash}_{hashlib.md5(response_json.encode()).hexdigest()[:8]}"
        temp_file = os.path.join(tempfile.gettempdir(), f"mcp_response_{file_id}.json")
        
        with open(temp_file, 'w') as f:
            f.write(response_json)
        
        self.temp_files[file_id] = {
            'file_path': temp_file,
            'total_size': len(response_json),
            'chunks_read': 0
        }
        
        return {
            'type': 'large_response',
            'file_id': file_id,
            'total_size': len(response_json),
            'summary': self._create_summary(response_data),
            'message': f"READ ALL CHUNKS!!!. Response too large ({len(response_json)} chars). Use read_response_chunk tool with file_id '{file_id}' to read in chunks. \
                Total chunks available: {(len(response_json) + self.MAX_CHUNK_SIZE - 1) // self.MAX_CHUNK_SIZE}. Be sure to read all chunks to get the full response."
        }
    
    def _create_summary(self, response_data):
        """Create a summary of the large response"""
        if isinstance(response_data, dict):
            summary = {}
            for key, value in response_data.items():
                if isinstance(value, str) and len(value) > 200:
                    summary[key] = f"{value[:200]}... [truncated, {len(value)} total chars]"
                elif isinstance(value, list):
                    summary[key] = f"[List with {len(value)} items]"
                elif isinstance(value, dict):
                    summary[key] = f"[Object with {len(value)} keys]"
                else:
                    summary[key] = value
            return summary
        return str(response_data)[:500] + "..." if len(str(response_data)) > 500 else response_data