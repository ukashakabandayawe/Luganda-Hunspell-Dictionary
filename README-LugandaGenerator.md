Luganda Affix Generator (JavaFX)

What this does
- Small JavaFX app that reads `Luganda.aff` in the current folder (or a file you choose), asks for the number of root words, accepts the root words, then generates possible prefixed forms from the `PFX` rules and shows them in a table. You can save results as CSV.

Build & run (basic, assuming JDK + JavaFX are installed)

Compile:
```powershell
cd "E:\Luganda Hunspell Dictionary"
javac -cp "PATH_TO_FX_LIBS/*" src\LugandaAffParser.java src\LugandaGeneratorApp.java
```

Run:
```powershell
java --module-path "PATH_TO_FX_LIBS" --add-modules javafx.controls,javafx.graphics -cp src LugandaGeneratorApp
```

Replace `PATH_TO_FX_LIBS` with the folder that contains JavaFX jars (for example the `lib` folder of an OpenJFX SDK).

Notes
- The parser is a simple parser tailored to the `PFX` format used in your provided `Luganda.aff`. It does not implement condition matching or SFX rules. It treats `0` as empty (no-strip or empty affix).
- If `Luganda.aff` is not found in the working directory the app lets you choose a different `.aff` file.
