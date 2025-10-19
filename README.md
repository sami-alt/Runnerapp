# Runnerapp

## Soveluksen toiminnot


*Käyttäjä pystyy luomaan tunnukset ja kirjautumaan sovelukseen. <br>
*Käyttäjä pystyy lisämään ja poistamaan juoksu suorituksia ja niiden dataa sovellukseen.<br>
*käyttäjä voi lisätä karttoja juoksu suorituksista.<br>
*Käyttäjä voi etsiä muita käyttäjiä ja heidän juoksu suorituksia ja kommentoida niitä.<br>
*Sovelluksessa on tilasto sivut suorituksista ja käyttäjistä.<br>
*Käyttäjä voi hakea suorituksista tietoa eri parametreilla.<br>
*Käyttäjä pystyy arvoimaan omia ja muiden suorituksia.<br>

## Sovelluksen asennus

flask run<br>
sqlite3 database.db < schema.sql<br>
sqlite3 database.db < init.sql<br>

Aplikaation testaukseen luo käyttäjä tunnukset <br>
Lisää suorituksia ja voit hakea niitä haku toiminnolla tai katsoa kaikkia suorituksia kerralla<br>
Tilastoja löytyy statistics linkin alta ja ne päivittyvät käyttäjien ja juoksujen määrän mukaan<br>
Käyttäjä voi lisätä itselleen profiili kuvan ja kuvia reitesitä joita hän on juossut<br>
Voidaan kommentoida omia ja muiden suorituksia<br>
Suorituksia voidaan muokata ja poistaa<br>