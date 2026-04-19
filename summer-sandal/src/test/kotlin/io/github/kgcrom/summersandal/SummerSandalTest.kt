package io.github.kgcrom.summersandal

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe

class SummerSandalTest : StringSpec({
    "placeholder type exposes the module name" {
        SummerSandal().name() shouldBe "summer-sandal"
    }
})
