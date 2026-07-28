package com.karna.companion.data

import android.content.ContentResolver
import android.net.Uri
import com.karna.companion.model.AnalysisResponse
import com.karna.companion.share.ImageValidator
import com.karna.companion.share.SharedTextRequest
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class KarnaRepository(private val apiFactory: (String) -> KarnaApi = ::createApi) {
    suspend fun analyzeText(baseUrl: String, text: String): Result<AnalysisResponse> = safeCall {
        apiFactory(validatedBaseUrl(baseUrl)).analyze(SharedTextRequest.from(text))
    }

    suspend fun analyzeImage(
        baseUrl: String,
        resolver: ContentResolver,
        uri: Uri,
        mimeType: String?,
    ): Result<AnalysisResponse> = safeCall {
        val size = resolver.openAssetFileDescriptor(uri, "r")?.use { it.length }
        ImageValidator.validate(mimeType, size)?.let { throw KarnaRequestException(it) }
        val bytes = resolver.openInputStream(uri)?.use { it.readBytes() }
            ?: throw KarnaRequestException("Karna could not read the shared image.")
        if (bytes.size > ImageValidator.maxBytes) throw KarnaRequestException("Image size must not exceed 5 MB.")
        val requestBody = bytes.toRequestBody(mimeType!!.toMediaType())
        val image = MultipartBody.Part.createFormData("image", "shared-image", requestBody)
        apiFactory(validatedBaseUrl(baseUrl)).analyzeImage(image)
    }

    private suspend fun <T> safeCall(action: suspend () -> T): Result<T> = try {
        Result.success(action())
    } catch (error: KarnaRequestException) {
        Result.failure(error)
    } catch (_: Exception) {
        Result.failure(KarnaRequestException("Karna is unavailable right now. Check your connection and try again."))
    }

    private fun validatedBaseUrl(value: String): String {
        val normalized = value.trim().trimEnd('/') + "/"
        if (!normalized.startsWith("https://")) {
            throw KarnaRequestException("Use an HTTPS Karna API address.")
        }
        return normalized
    }

    private companion object {
        fun createApi(baseUrl: String): KarnaApi = Retrofit.Builder()
            .baseUrl(baseUrl)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(KarnaApi::class.java)
    }
}

class KarnaRequestException(message: String) : Exception(message)
