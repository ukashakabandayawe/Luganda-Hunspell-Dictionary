module com.lugandahunspelldictionary {
    requires javafx.controls;
    requires javafx.fxml;

    opens com.lugandahunspelldictionary to javafx.fxml;
    exports com.lugandahunspelldictionary;
}
