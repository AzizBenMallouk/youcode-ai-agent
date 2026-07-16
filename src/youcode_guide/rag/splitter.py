from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


@dataclass
class ParentChildDocuments:
    parents: list[Document]
    children: list[Document]


def create_parent_splitter(
    chunk_size: int = 1200,
    chunk_overlap: int = 150,
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        add_start_index=True,
    )


def create_child_splitter(
    chunk_size: int = 300,
    chunk_overlap: int = 50,
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        add_start_index=True,
    )

def split_parent_child_documents(
    documents: list[Document],
    parent_chunk_size: int = 1200,
    parent_chunk_overlap: int = 150,
    child_chunk_size: int = 300,
    child_chunk_overlap: int = 50,
) -> ParentChildDocuments:
    parent_splitter = create_parent_splitter(
        chunk_size=parent_chunk_size,
        chunk_overlap=parent_chunk_overlap,
    )

    child_splitter = create_child_splitter(
        chunk_size=child_chunk_size,
        chunk_overlap=child_chunk_overlap,
    )

    all_parents: list[Document] = []
    all_children: list[Document] = []

    for source_document in documents:
        document_id = source_document.metadata[
            "document_id"
        ]

        parent_chunks = (
            parent_splitter.split_documents(
                [source_document]
            )
        )

        for parent_index, parent in enumerate(
            parent_chunks
        ):
            parent_id = (
                f"{document_id}:parent:"
                f"{parent_index}"
            )

            parent_start_index = (
                parent.metadata.pop(
                    "start_index",
                    None,
                )
            )

            parent.metadata.update(
                {
                    "chunk_type": "parent",
                    "parent_id": parent_id,
                    "parent_index": parent_index,
                    "parent_start_index": (
                        parent_start_index
                    ),
                }
            )

            all_parents.append(parent)

            child_chunks = (
                child_splitter.split_documents(
                    [parent]
                )
            )

            for child_index, child in enumerate(
                child_chunks
            ):
                child_id = (
                    f"{parent_id}:child:"
                    f"{child_index}"
                )

                child_start_index = (
                    child.metadata.pop(
                        "start_index",
                        None,
                    )
                )

                child.metadata.update(
                    {
                        "chunk_type": "child",
                        "child_id": child_id,
                        "child_index": child_index,
                        "parent_id": parent_id,
                        "parent_index": parent_index,
                        "child_start_index": (
                            child_start_index
                        ),
                    }
                )

                all_children.append(child)

    return ParentChildDocuments(
        parents=all_parents,
        children=all_children,
    )