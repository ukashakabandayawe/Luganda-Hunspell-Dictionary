''' powershell -NoProfile -ExecutionPolicy Bypass -File "e:\Luganda Hunspell Dictionary\scripts\clean_dict.ps1" '''

TO-DO: Using "eby'", or "eby" "Ow'", "Ey'" etc independent words in the .dic and MAY BE also adding the apostrophe as a valid character

Put the word in to consideration for verbs: Kugema, erigema, akagema, ekigema, agema, abagema, ebigema, agagema, okugema, obugema, okugemebwa, eyagemebwa, okugemwa, abagemebwa, abaagemebwa, akaagemebwa, erigemebwa, ekigemebwa, agemebwa, ebigemebwa, agagemebwa, agaagemebwa, akaligema, erinaagema, ekiligema, agaligema, anaagema, abaligema, ebiligema, agemeddwa, ekameddwa, abagemeddwa

Get-Content "e:\Luganda Hunspell Dictionary\Luganda.dic" | Measure-Object -Line