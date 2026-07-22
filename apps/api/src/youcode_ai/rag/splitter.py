from dataclasses import dataclass

from langchain_core.documents import (
    Document,
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from youcode_ai.core.config import (
    settings,
)


@dataclass
class ParentChildDocuments:
    parents: list[Document]
    children: list[Document]


def create_parent_splitter(
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=(
            settings
            .rag_parent_chunk_size
        ),
        chunk_overlap=(
            settings
            .rag_parent_chunk_overlap
        ),
        separators=[
            "\n# ",
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        add_start_index=True,
        strip_whitespace=True,
    )


def create_child_splitter(
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=(
            settings
            .rag_child_chunk_size
        ),
        chunk_overlap=(
            settings
            .rag_child_chunk_overlap
        ),
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        add_start_index=True,
        strip_whitespace=True,
    )


def split_parent_child_documents(
    documents: list[Document],
) -> ParentChildDocuments:
    parent_splitter = (
        create_parent_splitter()
    )

    child_splitter = (
        create_child_splitter()
    )

    parents: list[Document] = []
    children: list[Document] = []

    for source_document in documents:
        document_id = (
            source_document
            .metadata
            .get("document_id")
        )

        if not document_id:
            raise ValueError(
                "Source document has no "
                "document_id."
            )

        parent_chunks = (
            parent_splitter
            .split_documents(
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

            parent_metadata = {
                **parent.metadata,
                "chunk_type": "parent",
                "parent_id": parent_id,
                "parent_index": (
                    parent_index
                ),
            }

            if parent_start_index is not None:
                parent_metadata[
                    "parent_start_index"
                ] = parent_start_index

            parent_document = Document(
                page_content=(
                    parent.page_content
                ),
                metadata=parent_metadata,
            )

            parents.append(
                parent_document
            )

            child_chunks = (
                child_splitter
                .split_documents(
                    [parent_document]
                )
            )

            for (
                child_index,
                child,
            ) in enumerate(child_chunks):
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

                child_metadata = {
                    **child.metadata,
                    "chunk_type": "child",
                    "parent_id": parent_id,
                    "parent_index": (
                        parent_index
                    ),
                    "child_id": child_id,
                    "child_index": (
                        child_index
                    ),
                }

                if (
                    child_start_index
                    is not None
                ):
                    child_metadata[
                        "child_start_index"
                    ] = child_start_index

                    if (
                        parent_start_index
                        is not None
                    ):
                        child_metadata[
                            "global_start_index"
                        ] = (
                            parent_start_index
                            + child_start_index
                        )

                child_document = Document(
                    page_content=(
                        child.page_content
                    ),
                    metadata=child_metadata,
                )

                children.append(
                    child_document
                )

    return ParentChildDocuments(
        parents=parents,
        children=children,
    )