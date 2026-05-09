from accounts.serializers import GenerateRoutineSerializer

# Test 1: Valid payload
s = GenerateRoutineSerializer(data={'training_days': 3, 'training_weekdays': [1, 3, 5]})
print('Test 1 - Valid:', s.is_valid())
print('Errors:', s.errors)

# Test 2: Only training_days
s2 = GenerateRoutineSerializer(data={'training_days': 3})
print('\nTest 2 - Only training_days:', s2.is_valid())
print('Errors:', s2.errors)

# Test 3: Empty body
s3 = GenerateRoutineSerializer(data={})
print('\nTest 3 - Empty body:', s3.is_valid())
print('Errors:', s3.errors)

# Test 4: training_weekdays as empty list
s4 = GenerateRoutineSerializer(data={'training_days': 3, 'training_weekdays': []})
print('\nTest 4 - Empty weekdays:', s4.is_valid())
print('Errors:', s4.errors)
