# decapromolist

Decapromolist to prosty projekt, który stara się wyszukiwać atrakcyjnych okazji cenowych w sklepie internetowym www.decathlon.pl.

### Informacje
Skrypt parsuje zawartość strony w celu skatalogowania produktów sprzedawanych przez Decathlon w Polsce. Lista wynikowa przedstawia deltę (różnicę) między ostatnim uruchomieniem skryptu, a datą poprzedniego uruchomienia.

W ramach pojedynczego uruchomienia wykonanywane są następujące kroki:
* Sparsowanie kategorii
* Dla kazdej kategorii skanowane są dostępne produkty
* Wydobyte dane są przetwarzane i zapisywane do lokalnej bazy danych
* W wyniku przetwarzania zostają wyodrębnione oferty, które następnie są wzbogacane od dodatkowe informacje i zapisywane do listy wynikowej

Skrypt klasyfikuje zarówno przeceny promowane przez Decathlon (np. jako koniec serii), jak i obniżki cen, które nie są widoczne na stronie sklepu w formie przekreślonej ceny regularnej (początkowej).

Frontend, który pozwala na dosyć wygodne przeglądanie wygenerowanej listy, można znaleźć pod tym [adresem](https://rawgit.com/thof/decapromolist/master/decapromolist/decapromolist.html). Pozwala on na sortowanie i podstawowe filtrowanie wyników.

Nowe listy generowane są nieregularnie i w dużej mierze zależy to od zmian wprowadzanych przez Decathlon na stronie sklepu, które najczęściej sprawiają, że reguły parsowania decapromolist przestają działać i konieczna jest ich ręczna naprawa.

### Filtrowanie
Filtrowanie korzysta z uproszczonych wyrażeń regularnych. Przykłady:
* Pole "płeć" może przyjąc następujące wartości: M (męskie), F (damskie), J (dzieci), U (uniwersalne). Jeśli interesują nas tylko produkty dla mężczyzn i uniwersalne, wtedy można to zapisać jako *M|U* (dosłownie: męskie lub uniwersalne). A jeśli interesują nas wszystkie produkty poza męskimi, można to zapisać jako *F|U|J* lub *!M* (dosłownie: nie męskie)
* Jeśli w polu "kategoria" chcemy odfiltrować oferty związane z wędkowaniem, wtedy wystarczy wpisać *!wędk|!przenęty*, co można odczytać jako: odfiltruj wiersze, które zawierają kombinację "wędk" lub słowo "przynęty".
* Pola zawierające wartości liczbowe (cena regularne, cena, zniżka) mogą zawierać dodatkowo symbol "większe od" i "mniejsze od". Jeśli interesują nas oferty od obniżce większej niż 30%, wtedy należy założyć filtr o wartość *>30*

### Operacje

Można wyróżnić następujące operacje:
* [Nowa] - nowa przecena
* [Wyższa cena z XX.XX] - cena jest wyższa w stosunku do dnia poprzedniego
* [Niższa cena z XX.XX] - cena została obniżona w stosunku do dnia poprzedniego
* [Wycofana] - przecena produktu została wycofana (ta operacja nigdy nie pojawi się na liście, ale występuje w bazie danych)
* [Powrót] - wycofana wcześniej przecena wróciła i cena produktu nie zmieniła się
* [Powrót z wyższą ceną z XX.XX] - jak wyżej, ale wrócił z wyższą ceną
* [Powrót z niższą ceną z XX.XX] - jak wyżej, ale wrócił z niższą ceną
* [Obniżka] - tak oznaczane są produkty, których cena została obniżona w stosunku do ceny wcześniejszej, ale Decathlon nie informuje o tym, tj. brak jest przekreślonej ceny regularnej

## Szczegóły techniczne

Szczegóły dla osób chcących uruchomić skrypt na własnej maszynie.

### Zależności
* python2
* python2-lxml
* mysql-python

### Instalacja/uruchomienie
`python2 run.py`

### Konfiguracja
W katalogu *config* znajduje się przykładowy plik konfiguracyjny. Należy go poprawić, a potem zmienić nazwę na *config.json*.
Klucze, które mogą być niejasne:
* decapromolistDir - ścieżka do katalogu, w którym znajduje się projekt. Poprawna wartość jest wymagana tylko w przypadku automatycznego dodawania zmian do githuba. W przeciwnym wypadku pole jest opcjonalne,
* host - gdzie znajduje się baza danych MySQL,
* user - użytkownik bazodanowy,
* passwd - hasło,
* dbname - nazwa bazy MySQL.

### Baza danych
Struktura tabel bazy danych znajduje się w katalogu *dbschema*.

### decapromolist.json

W podkatalogu *decapromolist* znajdują się listy promowanych/przecenionych produktów. Aktualna lista znajduje się zawsze w pliku [decapromolist.json](https://raw.githubusercontent.com/thof/decapromolist/master/decapromolist/decapromolist.json). Kiedy zostaje on zastąpiony nowszym, jego nazwa zmienia się na *decapromolist_\<data\>.json*, gdzie *\<data\>* to dzień, w którym plik przestaje być aktualny. Listy mogą posłużyć jako źródła danych dla wygodnego front-endu.

### subcat.json

W podkatalogu *category* znajdują się listy kategorii wraz z podkategoriami. Plik [subcat.json](https://raw.githubusercontent.com/thof/decapromolist/master/category/subcat.json) zawiera najnowszą dostępną listę. Plik jest pomocny przy rozkodowywaniu podkategorii produktów.
