# decapromolist

Decapromolist to prosty projekt, który stara się wyszukiwać atrakcyjnych okazji cenowych w sklepie internetowym www.decathlon.pl.

### Zależności
* python2
* python2-lxml
* mysql-python

### Instalacja/uruchomienie
python2 run.py

### Konfiguracja
W katalogu *config* znajduje się przykładowy plik konfiguracyjny. Należy go poprawić, a potem zmienić nazwę na *config.json*.

### Baza danych
Struktura tabel bazy danych znajduje się w katalogu *dbschema*.

### decapromolist.json

W podkatalogu *decapromolist* znajdują się listy promowanych/przecenionych produktów. Aktualna lista znajduje się zawsze w pliku [decapromolist.json](https://raw.githubusercontent.com/thof/decapromolist/master/decapromolist/decapromolist.json). Kiedy zostaje on zastąpiony nowszym, jego nazwa zmienia się na *decapromolist_\<data\>.json*, gdzie *\<data\>* to dzień, w którym plik przestaje być aktualny. Listy mogą posłużyć jako źródła danych dla wygodnego front-endu.

Każdy rekord w pliku może zawierać następujące klucze (string):
* nm - name / nazwa
* rl - URL / adres internetowy
* sc - subcategory / podkategoria
* sz - size / tablica rozmiarów
* pr - price / cena
* op - old price / stara cena regularna
* dc - discount / obniżka w %
* pp - previous price / poprzednia cena (obniżona)
* or - operation / operacja
* rp - regular price / najniższa cena regularna
* rd - regular price date / data najniższej ceny regularnej

**Przykład wydruku:**
Kategoria: Jeździectwo->Wyposażenie jeźdźca

[Oficerki skórzane Victory S](http://www.decathlon.pl/oficerki-skorzane-victory-s-id_8206442.html) 649.99->259.99 (60%) [Powrót] [Rozmiary: 37, 38, 40, 41]

**Co odpowiada:** 
Kategoria: *cat['name']*->*cat['subName']*

*\[prod['nm']\]\(prod['rl']\)* *prod['op']*->*prod['pr']* \(*prod['dc']*) [*prod['or']*] [Rozmiary: *prod['sz']*]

### subcat.json

W podkatalogu *category* znajdują się listy kategorii wraz z podkategoriami. Plik [subcat.json](https://raw.githubusercontent.com/thof/decapromolist/master/category/subcat.json) zawiera najnowszą dostępną listę. Plik jest pomocny przy rozkodowywaniu podkategorii produktów.

Każdy rekord w pliku może zawierać następujące klucze (string):
* subId - ID podkategorii
* url - URL podkategorii
* subName - nazwa podkategorii
* id - ID kategorii
* name - nazwa kategorii

### Operacje

Można wyróżnić następujące operacje:
* [Nowa] - nowa przecena
* [Wyższa cena z XX.XX] - cena jest wyższa w stosunku do dnia poprzedniego
* [Niższa cena z XX.XX] - cena została obniżona w stosunku do dnia poprzedniego
* [Wycofana] - przecena produktu została wycofana (ta operacja nigdy nie pojawi się na liście, ale występuje w bazie danych)
* [Powrót] - wycofana wcześniej przecena wróciła i cena produktu nie zmieniła się
* [Powrót z wyższą ceną z XX.XX] - jak wyżej, ale wrócił z wyższą ceną
* [Powrót z niższą ceną z XX.XX] - jak wyżej, ale wrócił z niższą ceną
