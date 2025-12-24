''' powershell -NoProfile -ExecutionPolicy Bypass -File "e:\Luganda Hunspell Dictionary\scripts\clean_dict.ps1" '''

TO-DO: Using "eby'", or "eby" "Ow'", "Ey'" etc independent words in the .dic and MAY BE also adding the apostrophe as a valid character

Put the word in to consideration for verbs: Kugema, erigema, akagema, ekigema, agema, abagema, ebigema, agagema, okugema, obugema, okugemebwa, eyagemebwa, okugemwa, abagemebwa, abaagemebwa, akaagemebwa, erigemebwa, ekigemebwa, agemebwa, ebigemebwa, agagemebwa, agaagemebwa, akaligema, erinaagema, ekiligema, agaligema, anaagema, abaligema, ebiligema, agemeddwa, ekameddwa, abagemeddwa

Get-Content "e:\Luganda Hunspell Dictionary\Luganda.dic" | Measure-Object -Line

(Get-Content "Luganda.aff")[8..56]| Measure-Object -Line 
Replace the range in the square brackets 

$file = "Luganda.aff"; $start = 276; $end = 351; $char = "li";
$content = Get-Content $file;
for ($i = $start - 1; $i -lt $end -and $i -lt $content.Count; $i++) {
    $words = $content[$i] -split '\s+';                # Split line into words
    if ($words.Count -ge 4) {
        $words[3] += $char;                            # Add letter to 4th word (index 3)
        $content[$i] = $words -join ' ';               # Rejoin words
    }
}
$content | Set-Content $file