package com.lugandahunspelldictionary;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;

import java.util.*;

public class MajoritySetAnalyzer extends Application {

    private VBox setsContainer;
    private Spinner<Integer> setCountSpinner;
    private TextArea resultArea;

    private final List<TextField> nameFields = new ArrayList<>();
    private final List<TextArea> elementFields = new ArrayList<>();

    @Override
    public void start(Stage stage) {

        Label title = new Label("Set Majority Analyzer");
        title.setStyle("-fx-font-size:18px; -fx-font-weight:bold;");

        setCountSpinner = new Spinner<>(2, 10, 3);
        setCountSpinner.setEditable(true);

        Button createBtn = new Button("Create Sets");

        HBox topBox = new HBox(10,
                new Label("Number of Sets:"),
                setCountSpinner,
                createBtn);

        setsContainer = new VBox(10);

        createBtn.setOnAction(e ->
                generateSetInputs(setCountSpinner.getValue()));

        Button analyzeBtn = new Button("Analyze");

        resultArea = new TextArea();
        resultArea.setEditable(false);
        resultArea.setPrefHeight(300);

        analyzeBtn.setOnAction(e -> analyzeSets());

        VBox root = new VBox(15,
                title,
                topBox,
                new Separator(),
                setsContainer,
                analyzeBtn,
                resultArea);

        root.setPadding(new Insets(15));

        generateSetInputs(3);

        Scene scene = new Scene(new ScrollPane(root), 900, 700);

        stage.setTitle("Set Majority Analyzer");
        stage.setScene(scene);
        stage.show();
    }

    private void generateSetInputs(int count) {

        setsContainer.getChildren().clear();
        nameFields.clear();
        elementFields.clear();

        for (int i = 1; i <= count; i++) {

            TextField nameField = new TextField("Set " + i);

            TextArea elementsArea = new TextArea();
            elementsArea.setPrefRowCount(3);
            elementsArea.setPromptText(
                    "Enter elements separated by commas\nExample: apple, banana, mango");

            nameFields.add(nameField);
            elementFields.add(elementsArea);

            VBox box = new VBox(5,
                    new Label("Set " + i + " Name"),
                    nameField,
                    new Label("Elements"),
                    elementsArea);

            box.setStyle(
                    "-fx-border-color: lightgray;" +
                    "-fx-border-radius: 5;" +
                    "-fx-padding: 10;");

            setsContainer.getChildren().add(box);
        }
    }

    private void analyzeSets() {

        int totalSets = nameFields.size();

        Map<String, Integer> frequency = new TreeMap<>();

        for (TextArea area : elementFields) {

            Set<String> uniqueElements = new HashSet<>();

            String text = area.getText().trim();

            if (!text.isEmpty()) {

                String[] parts = text.split(",");

                for (String part : parts) {

                    String item = part.trim();

                    if (!item.isEmpty()) {
                        uniqueElements.add(item);
                    }
                }
            }

            for (String element : uniqueElements) {
                frequency.merge(element, 1, Integer::sum);
            }
        }

        StringBuilder sb = new StringBuilder();

        sb.append("TOTAL SETS: ")
          .append(totalSets)
          .append("\n\n");

        sb.append("ELEMENT FREQUENCIES\n");
        sb.append("===================\n");

        for (Map.Entry<String, Integer> entry : frequency.entrySet()) {
            sb.append(entry.getKey())
              .append(" -> ")
              .append(entry.getValue())
              .append(" set(s)\n");
        }

        sb.append("\n");

        sb.append("ELEMENTS APPEARING IN MORE THAN HALF OF THE SETS\n");
        sb.append("================================================\n");

        boolean foundMajority = false;

        for (Map.Entry<String, Integer> entry : frequency.entrySet()) {

            if (entry.getValue() > totalSets / 2.0) {

                sb.append(entry.getKey())
                  .append(" (")
                  .append(entry.getValue())
                  .append("/")
                  .append(totalSets)
                  .append(")\n");

                foundMajority = true;
            }
        }

        if (!foundMajority) {
            sb.append("None\n");
        }

        sb.append("\n");

        sb.append("ELEMENTS APPEARING IN LESS THAN HALF OF THE SETS\n");
        sb.append("================================================\n");

        boolean foundMinority = false;

        for (Map.Entry<String, Integer> entry : frequency.entrySet()) {

            if (entry.getValue() < totalSets / 2.0) {

                sb.append(entry.getKey())
                  .append(" (")
                  .append(entry.getValue())
                  .append("/")
                  .append(totalSets)
                  .append(")\n");

                foundMinority = true;
            }
        }

        if (!foundMinority) {
            sb.append("None\n");
        }

        resultArea.setText(sb.toString());
    }

    public static void main(String[] args) {
        launch(args);
    }
}