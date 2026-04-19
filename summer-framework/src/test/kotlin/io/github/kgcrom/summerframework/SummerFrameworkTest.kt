package io.github.kgcrom.summerframework

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe

class SummerFrameworkTest : StringSpec({
    "placeholder type exposes the module name" {
        SummerFramework().name() shouldBe "summer-framework"
    }
})

