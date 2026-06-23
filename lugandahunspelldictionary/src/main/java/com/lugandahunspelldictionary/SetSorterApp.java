package com.lugandahunspelldictionary;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SetSorterApp extends Application {

    @Override
    public void start(Stage stage) {

        TextArea inputArea = new TextArea();
        // inputArea.setPromptText("""
        //         Examples:
        //         BD,BE,BF,BG
        //         or
        //         BDBEBFBG
        //         or
        //         BD,BE,BFBD,BG
        //         """);

        TextArea outputArea = new TextArea();
        outputArea.setEditable(false);

        Button sortButton = new Button("Sort Elements");

        sortButton.setOnAction(e -> {
            String input = inputArea.getText();

            // Extract every 2-letter element
            Pattern pattern = Pattern.compile("[A-Za-z]{2}");
            Matcher matcher = pattern.matcher(input);

            Set<String> unique = new HashSet<>();

            while (matcher.find()) {
                unique.add(matcher.group());
            }

            List<String> sorted = new ArrayList<>(unique);

            sorted.sort((a, b) -> {
                int catA = category(a);
                int catB = category(b);

                if (catA != catB) {
                    return Integer.compare(catA, catB);
                }

                return a.compareTo(b);
            });

            outputArea.setText(String.join("", sorted));
        });

        VBox root = new VBox(10,
                new Label("Input Elements"),
                inputArea,
                sortButton,
                new Label("Sorted Output"),
                outputArea);

        root.setPadding(new Insets(15));

        Scene scene = new Scene(root, 700, 500);

        stage.setTitle("Set Element Sorter");
        stage.setScene(scene);
        stage.show();
    }

    private static int category(String s) {
        char c1 = s.charAt(0);
        char c2 = s.charAt(1);

        boolean firstUpper = Character.isUpperCase(c1);
        boolean secondUpper = Character.isUpperCase(c2);

        if (firstUpper && secondUpper) return 0;   // AA
        if (firstUpper) return 1;                  // Aa
        if (secondUpper) return 2;                 // aA
        return 3;                                  // aa
    }

    public static void main(String[] args) {
        launch(args);
    }
}