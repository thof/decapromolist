# decapromolist

W katalogu *product* znajdują się listy promowanych/przecenionych produktów. Aktualna lista znajduje się zawsze w pliku [product.json](https://raw.githubusercontent.com/thof/decapromolist/master/product/product.json). Kiedy zostaje on zastąpiony nowszym, jego nazwa zmienia się na *product_data.json*, gdzie *data* to dzień, w którym plik przestaje być aktualny.

Każdy rekord w pliku może zawierać następujące klucze (string):
* nm - name / nazwa
* rl - URL / adres internetowy
* sz - size / tablica rozmiarów
* pr - price / cena
* op - old price / stara cena regularna
* dc - discount / obniżka w %
* pp - previous price / poprzednia cena (obniżona)
* or - operation / operacja
* rp - regular price / najniższa cena regularna
* rd - regular price date / data najniższej ceny regularnej
