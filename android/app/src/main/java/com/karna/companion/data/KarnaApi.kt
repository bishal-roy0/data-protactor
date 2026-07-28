package com.karna.companion.data

import com.karna.companion.model.AnalysisResponse
import com.karna.companion.model.AnalyzeRequest
import okhttp3.MultipartBody
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface KarnaApi {
    @POST("analyze")
    suspend fun analyze(@Body request: AnalyzeRequest): AnalysisResponse

    @Multipart
    @POST("analyze/image")
    suspend fun analyzeImage(@Part image: MultipartBody.Part): AnalysisResponse
}
