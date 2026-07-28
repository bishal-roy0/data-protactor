package com.karna.companion.share

import android.content.Intent
import android.net.Uri
import androidx.core.content.IntentCompat

sealed interface SharedContent {
    data object Empty : SharedContent
    data class Text(val value: String) : SharedContent
    data class Image(val uri: Uri, val mimeType: String?) : SharedContent
}

object SharedContentParser {
    fun fromIntent(intent: Intent?): SharedContent {
        if (intent?.action != Intent.ACTION_SEND) return SharedContent.Empty

        val mimeType = intent.type
        if (mimeType == "text/plain") {
            val text = intent.getCharSequenceExtra(Intent.EXTRA_TEXT)?.toString()?.trim().orEmpty()
            return if (text.isBlank()) SharedContent.Empty else SharedContent.Text(text)
        }

        if (mimeType?.startsWith("image/") == true) {
            val uri = IntentCompat.getParcelableExtra(intent, Intent.EXTRA_STREAM, Uri::class.java)
            return if (uri == null) SharedContent.Empty else SharedContent.Image(uri, mimeType)
        }
        return SharedContent.Empty
    }
}
