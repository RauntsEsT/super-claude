---
name: kotlin-patterns
description: Idiomatic Kotlin patterns, best practices, and conventions for building robust, efficient, and maintainable Kotlin applications with coroutines, null safety, and DSL builders.
origin: ECC
---

# Kotlin Development Patterns

Idiomatic Kotlin patterns and best practices.

## When to Use

- Writing new Kotlin code
- Reviewing Kotlin code
- Refactoring existing Kotlin code

## Core Principles

### Null Safety
```kotlin
fun getUserEmail(userId: String): String {
    val user = userRepository.findById(userId)
    return user?.email ?: "unknown@example.com"
}
```

### Immutability
```kotlin
data class User(val id: String, val name: String, val email: String)
fun updateEmail(user: User, newEmail: String): User = user.copy(email = newEmail)
```

### Sealed Classes
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Failure(val error: AppError) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}
```

### Structured Concurrency
```kotlin
suspend fun fetchUserWithPosts(userId: String): UserProfile =
    coroutineScope {
        val user = async { userService.getUser(userId) }
        val posts = async { postService.getUserPosts(userId) }
        UserProfile(user = user.await(), posts = posts.await())
    }
```

### Scope Functions
```kotlin
val user = User().apply { name = "Alice"; email = "alice@example.com" }
val result = createUser(request).also { logger.info("Created: ${it.id}") }
```

### Extension Functions
```kotlin
fun String.toSlug(): String =
    lowercase().replace(Regex("[^a-z0-9\\s-]"), "").replace(Regex("\\s+"), "-").trim('-')
```

## Anti-Patterns
- Force-unwrapping: `user!!.name` — use safe calls instead
- `GlobalScope.launch` — use structured concurrency
- Mutable data classes
- Using exceptions for control flow
