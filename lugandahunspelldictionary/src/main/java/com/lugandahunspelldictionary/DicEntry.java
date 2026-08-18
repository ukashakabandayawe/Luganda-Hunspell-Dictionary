package com.lugandahunspelldictionary;

import javafx.beans.property.BooleanProperty;
import javafx.beans.property.SimpleBooleanProperty;

import java.util.Set;

public final class DicEntry {
    private final String stem;
    private final String flagsRaw;
    private final String trailing;
    private final String category;
    private final BooleanProperty checked;

    public DicEntry(String stem, String flagsRaw, String trailing) {
        this(stem, flagsRaw, trailing, "");
    }

    public DicEntry(String stem, String flagsRaw, String trailing, String category) {
        this.stem = stem == null ? "" : stem.trim();
        this.flagsRaw = flagsRaw == null ? "" : flagsRaw.trim();
        this.trailing = trailing == null ? "" : trailing;
        this.category = category == null ? "" : category.trim();
        this.checked = new SimpleBooleanProperty(false);
    }

    public String getStem() {
        return stem;
    }

    public String getFlagsRaw() {
        return flagsRaw;
    }

    public String getTrailing() {
        return trailing;
    }

    public String getCategory() {
        return category;
    }

    public BooleanProperty checkedProperty() {
        return checked;
    }

    public boolean isChecked() {
        return checked.get();
    }

    public void setChecked(boolean value) {
        checked.set(value);
    }

    public int getFlagTokenCount(CommonFlagAnalyzer.FlagMode mode) {
        return getNormalizedFlags(mode).size();
    }

    public Set<String> getNormalizedFlags(CommonFlagAnalyzer.FlagMode mode) {
        return CommonFlagAnalyzer.normalizeFlags(flagsRaw, mode);
    }

    public String getNormalizedFlagsText(CommonFlagAnalyzer.FlagMode mode) {
        return CommonFlagAnalyzer.formatFlags(getNormalizedFlags(mode), mode);
    }

    @Override
    public String toString() {
        return stem;
    }
}