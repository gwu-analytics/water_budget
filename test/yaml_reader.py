import yaml

with open('../sample_data.yaml', 'r') as file:
    data = yaml.safe_load(file)

print(data)
print(data[0]['meters'])

for i in data:
     print(f'Area: {i['irrigatableArea']} square feet', f'Meters: {i['meters']}')