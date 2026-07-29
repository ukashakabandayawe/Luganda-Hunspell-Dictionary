package com.lugandahunspelldictionary;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.util.LinkedHashSet;
import java.util.Set;

public class SetOperationsFX extends Application {

    @Override
    public void start(Stage stage) {

        Label lbl1 = new Label("Set 1 (comma separated):");
        TextArea set1Input = new TextArea();
        set1Input.setPromptText("Example:\nBL, BM, BU, EC, EG");

        Label lbl2 = new Label("Set 2 (comma separated):");
        TextArea set2Input = new TextArea();
        set2Input.setPromptText("Example:\nBM, EC, FK, RP");

        Button processBtn = new Button("Process");

        TextArea output = new TextArea();
        output.setEditable(false);
        output.setPrefHeight(220);

        processBtn.setOnAction(e -> {

            Set<String> set1 = parseSet(set1Input.getText());
            Set<String> set2 = parseSet(set2Input.getText());

            if (set1.isEmpty() || set2.isEmpty()) {
                output.setText("Please enter valid elements for both sets.\n"
                        + "Each element must contain exactly 2 characters.");
                return;
            }

            Set<String> intersection = new LinkedHashSet<>(set1);
            intersection.retainAll(set2);

            Set<String> unique1 = new LinkedHashSet<>(set1);
            unique1.removeAll(set2);

            Set<String> unique2 = new LinkedHashSet<>(set2);
            unique2.removeAll(set1);

            StringBuilder sb = new StringBuilder();

            sb.append("Set 1:\n")
              .append(set1)
              .append("\n\n");

            sb.append("Set 2:\n")
              .append(set2)
              .append("\n\n");

            sb.append("Intersection:\n")
              .append(intersection)
              .append("\n\n");

            sb.append("Unique to Set 1:\n")
              .append(unique1)
              .append("\n\n");

            sb.append("Unique to Set 2:\n")
              .append(unique2);

            output.setText(sb.toString());
        });

        VBox root = new VBox(10,
                lbl1,
                set1Input,
                lbl2,
                set2Input,
                processBtn,
                output);

        root.setPadding(new Insets(15));

        Scene scene = new Scene(root, 600, 600);

        stage.setTitle("JavaFX Set Operations");
        stage.setScene(scene);
        stage.show();
    }

    private Set<String> parseSet(String text) {

        Set<String> set = new LinkedHashSet<>();

        if (text == null || text.trim().isEmpty())
            return set;

        String[] parts = text.split(",");

        for (String part : parts) {
            String value = part.trim();

            // Accept only elements with exactly 2 characters
            if (value.length() == 2) {
                set.add(value);
            }
        }

        return set;
    }

    public static void main(String[] args) {
        launch(args);
    }
}
