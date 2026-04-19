plugins {
    base
}

allprojects {
    version = "0.1.0-SNAPSHOT"
}

subprojects {
    repositories {
        mavenCentral()
    }

    pluginManager.withPlugin("org.jetbrains.kotlin.jvm") {
        tasks.withType(Test::class.java).configureEach {
            useJUnitPlatform()
        }
    }

    pluginManager.withPlugin("java-library") {
        extensions.configure<JavaPluginExtension> {
            toolchain {
                languageVersion.set(JavaLanguageVersion.of(21))
            }
            withJavadocJar()
            withSourcesJar()
        }
    }
}
