import requests

## Запрос на создание юзера
# response = requests.post("http://127.0.0.1:8080/user/",
#                          json={'name': "user_5", "password": "pass_5"}
#                          )

# # Запрос на создание объявления
# response = requests.post("http://127.0.0.1:8080/ads/",
#                          json={"header": "ad_3",
#                                "description": "description_3",
#                                "owner_id": "4"}
#                          )

# # Запрос на создание объявления
# response = requests.get("http://127.0.0.1:8080/ads/2/")

# Запрос на удаление объявления
response = requests.delete("http://127.0.0.1:8080/ads/2/")

print(response.status_code)
print(response.text)