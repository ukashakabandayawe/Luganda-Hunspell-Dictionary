package com.luganda.offlinereview.ui;

import android.content.Context;
import android.content.res.TypedArray;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.util.TypedValue;
import android.view.View;

import androidx.annotation.ColorInt;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;

import com.google.android.material.color.MaterialColors;
import com.luganda.offlinereview.R;

/**
 * Lightweight donut/ring chart (no external deps).
 *
 * Call {@link #setValues(int, int, int)} to update.
 */
public class DonutProgressView extends View {

    private final Paint ringPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint segmentPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF arcRect = new RectF();

    private int active;
    private int inactive;
    private int drafts;

    private float strokeWidthPx;

    @ColorInt private int ringColor;
    @ColorInt private int activeColor;
    @ColorInt private int inactiveColor;
    @ColorInt private int draftsColor;

    public DonutProgressView(Context context) {
        this(context, null);
    }

    public DonutProgressView(Context context, @Nullable AttributeSet attrs) {
        this(context, attrs, 0);
    }

    public DonutProgressView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);

        strokeWidthPx = dp(14);

        ringColor = MaterialColors.getColor(this, com.google.android.material.R.attr.colorSurfaceVariant);
        activeColor = ContextCompat.getColor(context, R.color.success_green);
        inactiveColor = MaterialColors.getColor(this, com.google.android.material.R.attr.colorError);
        draftsColor = MaterialColors.getColor(this, com.google.android.material.R.attr.colorSecondary);

        if (attrs != null) {
            TypedArray a = context.obtainStyledAttributes(attrs, new int[]{});
            a.recycle();
        }

        ringPaint.setStyle(Paint.Style.STROKE);
        ringPaint.setStrokeCap(Paint.Cap.ROUND);
        ringPaint.setStrokeWidth(strokeWidthPx);
        ringPaint.setColor(ringColor);

        segmentPaint.setStyle(Paint.Style.STROKE);
        segmentPaint.setStrokeCap(Paint.Cap.ROUND);
        segmentPaint.setStrokeWidth(strokeWidthPx);
    }

    public void setValues(int active, int inactive, int drafts) {
        this.active = Math.max(0, active);
        this.inactive = Math.max(0, inactive);
        this.drafts = Math.max(0, drafts);
        invalidate();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        float pad = strokeWidthPx / 2f;
        arcRect.set(pad, pad, w - pad, h - pad);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // Background ring
        canvas.drawArc(arcRect, 0f, 360f, false, ringPaint);

        int total = active + inactive + drafts;
        if (total <= 0) return;

        float start = -90f;

        // Draw segments (skip zero values)
        start = drawSegment(canvas, start, active, total, activeColor);
        start = drawSegment(canvas, start, inactive, total, inactiveColor);
        drawSegment(canvas, start, drafts, total, draftsColor);
    }

    private float drawSegment(Canvas canvas, float start, int value, int total, @ColorInt int color) {
        if (value <= 0) return start;

        float sweep = 360f * (value / (float) total);

        segmentPaint.setColor(color);
        canvas.drawArc(arcRect, start, sweep, false, segmentPaint);
        return start + sweep;
    }

    private float dp(float v) {
        return TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, getResources().getDisplayMetrics());
    }
}
