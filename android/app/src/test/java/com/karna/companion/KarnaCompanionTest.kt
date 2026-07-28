package com.karna.companion

import com.karna.companion.data.KarnaRepository
import com.karna.companion.model.AnalysisResponse
import com.karna.companion.share.ImageValidator
import com.karna.companion.share.SharedTextRequest
import com.karna.companion.ui.SafetyResultPresenter
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Test
import java.io.IOException

class KarnaCompanionTest {
    @Test
    fun `shared URL becomes a URL analysis request`() {
        val request = SharedTextRequest.from("https://example.test/update.exe")

        assertEquals(listOf("https://example.test/update.exe"), request.urls)
        assertNull(request.text)
    }

    @Test
    fun `shared message becomes a text analysis request`() {
        val request = SharedTextRequest.from("Urgent: verify your account now")

        assertEquals("Urgent: verify your account now", request.text)
        assertEquals(emptyList<String>(), request.urls)
    }

    @Test
    fun `unsupported image type is rejected before upload`() {
        assertEquals("Only JPG, PNG, and WEBP images are supported.", ImageValidator.validate("image/gif", 1_000))
    }

    @Test
    fun `oversized image is rejected before upload`() {
        assertEquals("Image size must not exceed 5 MB.", ImageValidator.validate("image/png", ImageValidator.maxBytes + 1))
    }

    @Test
    fun `api failures return a privacy safe message`() = runTest {
        val repository = KarnaRepository { throw IOException("network details must not be shown") }

        val result = repository.analyzeText("https://api.example/", "hello")

        assertFalse(result.isSuccess)
        assertEquals("Karna is unavailable right now. Check your connection and try again.", result.exceptionOrNull()?.message)
    }

    @Test
    fun `unknown server actions render as show caution`() {
        val result = AnalysisResponse("safe", 0, "safe", emptyList(), 0.5, "unexpected", "No signals")

        assertEquals("show caution", SafetyResultPresenter.actionLabel(result))
    }
}
