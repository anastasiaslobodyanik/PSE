1. Wann ist die Deadline? 
> 22.11 - Pflichtenheft-Abgabe und Präsentation

2. Soll das Pflichtenheft eine Einleitung beinhalten? 
> ganz grob

3. Darf Text direkt von der Website kopiert werden?
> Ja und kennzeichnen

4. Werden Benutzer in Gruppen eingeteilt? Wie werden Gruppen definiert (z.B. Institutszugehörigkeit)? Wer kann Gruppen erstellen? Wie werden Rollen in den Gruppen verteilt? Wie viele Administratoren kann eine Gruppe haben? Welche gruppenbezogenen Daten sind zu speichern? Ist Administratorstatus gruppenbezogen oder allgemein gültig? Wer kann eine Gruppe erstellen?(jeder Benutzer? oder institut-Verantwortlicher?)
Wie wird einen Benutzer zu einer Gruppe eingeladen?(per Email?) Kann Benutzer nach Gruppen suchen und selber ein Request dazu senden? Oder nur Admin einer Gruppe darf einen Benutzer zur Gruppe einladen?
> Es sind keine Gruppen vorgesehen. Eine Gruppe entsteht durch gemeinsame Rechte auf Ressourcen. Dabeisoll es möglich sein, mehrere Ressourcen einer Gruppe zu veröffentlichen, ohne jedes Mal alle Teilnehmer auswählen zu müssen *facepalm*

5. Gibt es Unterschiede zwischen Ressourcen und Daten?
> Ressourcen sollen als eine Abstraktion implementiert werden, so dass diese Implementierung an Daten allen Typen eingesetzt werden kann. Wir sollen für unsere Tests eine Beispieltabelle erstellen.

6. Ressourcen sind nur sichtbar, wenn Benutzer entsprechende Rechte besitzen. Wie können Rechte auf Ressourcen erlangt werden? 
> Meta-Daten für jeden zugänglich. Wir sollen Annehmen, dass Nutzer über Existenz von Daten wissen. Daten sind auch ohne Leserechte zu sehen, aber nicht zu lesen. Es kann auch Ressourcen geben, dessen Metadaten nur beschränkt zu sehen sind. (Ich denk, dass bedeutet, dass man seine Daten unvisible machen kann (Anastasia))

7. Sind Benutzer in der Lage, persönliche Informationen selbst zu ändern? Wenn ja, welche? Wie werden IDs erworben? 
> Ja,E-Mail. IDs nicht. Ne doch nichts ändern. ID - String

8. Sind Registrierungs-, An- und Abmeldeverfahren bereits implementiert? 
> Anmeldung ja. Wir sollen annehmen, dass alles schon existiert. 

9. Ist die Datenverwaltung bereits implementiert?
> Same. Dazu noch: man soll Rechte unterscheiden: lesen, ausfüren (für Tools). Ressourcen-Abstraktion: es soll einfach sein, neue Art von Ressourcen zu definieren

10. Was sind Anforderungen für Speicherkapazität und Antwortzeiten des Systems?
> Keine. Alles soll sinnvoll sein.

11. An welche Zielgruppen ist das Produkt gerichtet? Nur Mitarbeiter von V-FOR-WaTer? 
> Nutzer von V-FOR-WaTer(externe); Mitarbeiter sind Admins. Registrieren kann jeder (keine Einladungen), default sind public Daten zu sehen

12. Was sind die Software/Hardware-Anforderungen bez. des Produkts? 
> moderne Browser(Chrome,Firefox,Edge,Safari); Standartrechner

13. Führt das Versagen eines Requests zur automatischen Wiederholung? 
> Serverseitige Log-Files. Mehrere Versuche ohne Erfolg - emmail an Admin

14. Sollen Hilfeverweise für Benutzer zur Verfügung gestellt werden? 
> Hower Tipps(kurz) für Buttons und Felder

15. Koennen die Benutzer miteinander kommunizieren?(wie in ILIAS per Email?wenn ja,dann haben die Benutzer auch  Inbox, outbox...?) 
> Nein, nicht unterstützt; Die Benutzer kennen die E-Mails von anderen Benutzern nicht; beim Request - Name und E-Mail sichtbar für Ressourcenbesitzer

16. Wo sollte diesen Token reingebracht werden?
> Wir sollen entscheiden, ob wir das machen. Falls ja, habe ich Skizze von Jörg (Anastasia)

17. Sonstiges
> 15 min für Präsentation. Entwerder Phasenverantwortliche oder alle zusammen, soll aber gut strukturiert sein
> Wunschkriterium: Request um admin zu sein.
> Beim löschen alle Besitzer werden benachrichtig
> Besitzer kann mehrere Besitzrechte vergeben - mehrere Besitzer für ein Ressource möglich
> Daten ändern = neuen (geänderten) Datenbestand hochladen & alten löschen


