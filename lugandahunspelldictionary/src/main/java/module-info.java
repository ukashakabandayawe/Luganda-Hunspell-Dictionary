module com.lugandahunspelldictionary {
    requires transitive javafx.graphics;
    requires javafx.controls;
    requires javafx.fxml;
    requires java.prefs;

    opens com.lugandahunspelldictionary to javafx.fxml;
    exports com.lugandahunspelldictionary;
}
