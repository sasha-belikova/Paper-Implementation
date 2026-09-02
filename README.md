my_graph_dsl_project/
├── spec/                      # Спецификация языка и документация
│   ├── grammar.md             # Формальная грамматика (EBNF) для твоих конструкций
│   ├── types.md               # Описание типов (Matrix, Vector) и полуколец (bool, real)
│   └── semantics.md           # Описание работы операций (reach, pickAny и т.д.)
│
├── examples/                  # Примеры программ на твоем DSL (файлы с расширением .galg)
│   ├── reach.galg             # Твоя функция: func Reach(...)
│   ├── scc.galg               # Функция поиска сильно связанных компонент
│   └── wcc.galg               # Функция слабо связанных компонент
│
├── compiler/                  # Исходный код компилятора / парсера (если планируешь писать)
│   ├── parser.py              # Парсер синтаксиса DSL
│   └── core.py                # Трансляция в ядро
│
├── prototypes/                # Твои рабочие скрипты на Python (scipy.sparse и др.)
│   ├── graph_algorithms.py    # Реализация SCC, WCC и Reach на scipy.sparse
│   └── test_prototypes.py     # Проверка и запуск тестов
│
└── tests/                     # Автоматические тесты для проверки кода и грамматики