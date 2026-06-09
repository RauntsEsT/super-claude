---
name: kotlin-coroutines-flows
description: Kotlin Coroutines and Flow patterns for Android and KMP — structured concurrency, Flow operators, StateFlow, error handling, and testing.
origin: ECC
---

# Kotlin Coroutines & Flows

Patterns for structured concurrency, Flow-based reactive streams, and coroutine testing.

## When to Activate

- Writing async code with Kotlin coroutines
- Using Flow, StateFlow, or SharedFlow for reactive data
- Handling concurrent operations (parallel loading, debounce, retry)
- Testing coroutines and Flows

## Structured Concurrency

Always use structured concurrency — never `GlobalScope`:

```kotlin
// BAD
GlobalScope.launch { fetchData() }

// GOOD
viewModelScope.launch { fetchData() }
```

### Parallel Decomposition
```kotlin
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val items = async { itemRepository.getRecent() }
    val stats = async { statsRepository.getToday() }
    val profile = async { userRepository.getCurrent() }
    Dashboard(items = items.await(), stats = stats.await(), profile = profile.await())
}
```

## StateFlow for UI State

```kotlin
val progress: StateFlow<UserProgress> = observeProgress()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = UserProgress.EMPTY
    )
```

## Flow Operators

```kotlin
searchQuery
    .debounce(300)
    .distinctUntilChanged()
    .flatMapLatest { query -> repository.search(query) }
    .catch { emit(emptyList()) }
    .collect { results -> _state.update { it.copy(results = results) } }
```

## SharedFlow for One-Time Events

```kotlin
private val _effects = MutableSharedFlow<Effect>()
val effects: SharedFlow<Effect> = _effects.asSharedFlow()
```

## Dispatchers

```kotlin
withContext(Dispatchers.Default) { parseJson(largePayload) }
withContext(Dispatchers.IO) { database.query() }
```

## Anti-Patterns
- `GlobalScope` — leaks coroutines
- Catching `CancellationException` — let it propagate
- `MutableStateFlow` with mutable collections — use immutable copies
