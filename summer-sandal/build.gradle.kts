plugins {
    alias(libs.plugins.kotlin.jvm)
    `java-library`
    `maven-publish`
}

group = "io.github.kgcrom.summersandal"

kotlin {
    jvmToolchain(21)
}

dependencies {
    api(project(":summer-framework"))

    testImplementation(platform(libs.kotest.bom))
    testImplementation(libs.kotest.assertions.core)
    testImplementation(libs.kotest.runner.junit5)
}
