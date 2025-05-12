from flask import Blueprint, jsonify
from services.test_service import TestService

test_api = Blueprint('test_api', __name__)

# will be accessible through GET api/v1/test
@test_api.route('', methods=['GET'])
def test():
    result = TestService.test_backend()

    if result:
        return jsonify({'success': True, 'message': 'Server is responding!'}), 200
    else: 
        return jsonify({'success': False, 'message': 'Something went wrong!'}), 500