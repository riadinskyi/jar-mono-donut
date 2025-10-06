## Mono Jar Donut

### ßeta Open Banking рішення для клієнтів Monobank.  
> [!NOTE]
> Волонтерський API агрегатор для автоматичної обробки донацій, що надійшли на рахунок банки.
>
> 🇺🇦 Продукт послуговується для місії провадження **Open banking в Україні 🇺🇦**
> 
> Джерелом данних є офіційне АПІ Монобанк.


### 💸 Support projct
<a href="https://send.monobank.ua/jar/6dpG1MjjQb" target="_blank"><img alt="Support developer with Monobank donation" height="41" src="https://github.com/riadinskyi/city-alert-registry/blob/master/support-with-monobank-git.png?raw=true" title="Button for author support page" width="180"/></a>


## Important 

> [!Warning]
> Доступ до API та використання його вмісту здійснюються **виключно на власний розсуд і ризик**.  
> **Розробник за жодних обставин не несе відповідальності** перед будь-якою стороною за будь-які прямі, непрямі, випадкові, особливі чи інші збитки, що можуть виникнути внаслідок використання програмного забезпечення.
>
> Це програмне забезпечення підключається до Monobank API та автоматично обробляє фінансові транзакції для спрощення управління замовленнями. **Користувач несе повну відповідальність за правильність використання даних, проведені операції та дотримання чинного законодавства.**

> [!CAUTION]
> Використання програмного забезпечення для шахрайства, уникнення оподаткування, відмивання коштів або будь-яких інших незаконних дій **може призвести до кримінальної або адміністративної відповідальності** відповідно до законодавства України та інших внутрішніх і іноземних юрисдикцій.
>
> Розробник закликає користувачів офіційно реєструвати власну підприємницьку діяльність та сплачувати всі необхідні податки й обов’язкові внески до державних органів.
>
> Використовуючи програмний продукт, ви автоматично погоджуєтесь брати на себе повну відповідальність за всі наслідки, що можуть виникнути під час його застосування.


## ⚠️ Requirements
- Python 3.9+
- Poetry
- RSA keys
- Токен розробника від [Монобанк](https://monobank.ua/api-docs/monobank)

# Env settings
- SYSTEM_TOKEN — Токен для створення адміністраторів та випуску дозволів, від імені системи. (наприклад, коли ще немає жодного адміністратора)
- OPERATION_TOKEN — простий рядок, що використовується для авторизації доступу до кінцевих точок оплати через спеціальний заголовок, наприклад, для іншого API.

## Payments authorization
All /payment endpoints require a custom header with a plain token from env:

- Header: X-Operation-Token: <OPERATION_TOKEN>

Example:

```bash
curl -H "X-Operation-Token: $OPERATION_TOKEN" \
     "http://localhost:8000/api/v1/payment/get/by-id?payment_id=1"
```




## Generate PEM keys
```Shell
### Generate A RSA private key, size 2048 
openssl genrsa -out jwt-private.pem 2048
```
```shell
### Generate A RSA public key from the private key, which can be used in certification
openssl rsa -in jwt-private.pem -pubout -out jwt-public.pem
```

