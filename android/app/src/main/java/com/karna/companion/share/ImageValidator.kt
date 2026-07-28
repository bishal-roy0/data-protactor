package com.karna.companion.share

object ImageValidator {
    const val maxBytes = 5 * 1024 * 1024L
    private val allowedTypes = setOf("image/jpeg", "image/png", "image/webp")

    fun validate(mimeType: String?, sizeBytes: Long?): String? = when {
        mimeType !in allowedTypes -> "Only JPG, PNG, and WEBP images are supported."
        sizeBytes == null || sizeBytes < 0 -> "Karna could not verify the image size. Choose another image."
        sizeBytes > maxBytes -> "Image size must not exceed 5 MB."
        else -> null
    }
}
