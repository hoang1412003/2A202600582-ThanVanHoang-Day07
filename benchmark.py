import os
from pathlib import Path
from src import Document, EmbeddingStore, KnowledgeBaseAgent, FixedSizeChunker, _mock_embed

def parse_fm(text):
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm_text = parts[1]
    content = parts[2]
    meta = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, content

data_dir = Path("data")
files = [f for f in data_dir.glob("0*.md")]

docs = []
for f in files:
    text = f.read_text(encoding="utf-8")
    meta, content = parse_fm(text)
    docs.append(Document(id=f.stem, content=content.strip(), metadata=meta))

# 1. Compare Chunking Strategies (Baseline)
print("=== BASELINE ANALYSIS ===")
from src import ChunkingStrategyComparator
comparator = ChunkingStrategyComparator()
for doc in docs[:2]:
    print(f"Doc: {doc.id}")
    stats = comparator.compare(doc.content, chunk_size=500)
    for strategy, stat in stats.items():
        print(f"  {strategy}: {stat['count']} chunks, avg len {stat['avg_length']:.1f}")
print("\n")

# 2. Chunking with FixedSizeChunker
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunked_docs = []
for doc in docs:
    chunks = chunker.chunk(doc.content)
    for i, c in enumerate(chunks):
        chunked_docs.append(Document(id=f"{doc.id}_{i}", content=c, metadata=doc.metadata))

# 3. Store
store = EmbeddingStore(collection_name="benchmark_run", embedding_fn=_mock_embed)
store.add_documents(chunked_docs)

# 4. Agent
def mock_llm(prompt):
    return "LLM_MOCK_ANSWER"

agent = KnowledgeBaseAgent(store=store, llm_fn=mock_llm)

# 5. Queries
queries = [
    {
        "q": "Hồ Chí Minh tên khai sinh là gì và sinh năm nào?",
        "gold": "Tên khai sinh là Nguyễn Sinh Cung, sinh năm 1890.",
        "filter": None
    },
    {
        "q": "Quê quán và gia đình của Hồ Chí Minh có những thông tin chính nào?",
        "gold": "Quê nội làng Kim Liên, quê ngoại làng Hoàng Trù. Cha là Nguyễn Sinh Sắc, mẹ là Hoàng Thị Loan.",
        "filter": {"topic": "family_background"}
    },
    {
        "q": "Vì sao Nguyễn Tất Thành rời Việt Nam năm 1911?",
        "gold": "Để sang phương Tây tìm hiểu và tìm con đường cứu nước mới do các phong trào trước đều thất bại.",
        "filter": None
    },
    {
        "q": "Hồ Chí Minh có vai trò gì trong Cách mạng Tháng Tám và sự ra đời nước Việt Nam Dân chủ Cộng hòa?",
        "gold": "Lãnh đạo phong trào, soạn thảo và đọc Tuyên ngôn Độc lập năm 1945 khai sinh ra nước VNDCCH.",
        "filter": None
    },
    {
        "q": "Ngoài hoạt động chính trị, Hồ Chí Minh còn có đóng góp gì về văn hóa?",
        "gold": "Ông là nhà văn, nhà thơ, nhà báo, sáng tác nhiều tác phẩm bằng tiếng Việt, Pháp và Hán.",
        "filter": None
    }
]

print("=== BENCHMARK RESULTS ===")
for i, q in enumerate(queries):
    if q["filter"]:
        results = store.search_with_filter(q["q"], top_k=3, metadata_filter=q["filter"])
    else:
        results = store.search(q["q"], top_k=3)
    
    top_chunk = results[0]['content'][:100].replace('\n', ' ') + "..." if results else "None"
    score = results[0]['score'] if results else 0
    
    print(f"Q{i+1}: {q['q']}")
    print(f"Top-1 Chunk: {top_chunk}")
    print(f"Score: {score:.4f}")
    print(f"Relevant: {'Yes' if results else 'No'}")
    print()
