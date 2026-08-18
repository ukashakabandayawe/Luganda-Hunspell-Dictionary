module com.lugandahunspelldictionary {
    requires transitive javafx.graphics;
    requires javafx.controls;
    requires javafx.fxml;
    requires java.prefs;
    requires org.carrot2.morfologik.fsa;
    requires org.carrot2.morfologik.fsa_builders;
    requires hppc;

    opens com.lugandahunspelldictionary to javafx.fxml;
    exports com.lugandahunspelldictionary;
}
