import pandas as pd
import re
import pypdf
import featureform as ff
from featureform import local

def clean_text(text):
    # Remove numbers that appear randomly using regular expressions
    cleaned_text = re.sub(r'\b\d+\b', '', text)  # Remove standalone numbers
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple whitespaces with a single whitespace
    cleaned_text = cleaned_text.strip()  # Remove leading/trailing whitespaces
    return cleaned_text

def parse_pdf_paragraphs(pdf_path):
    paragraphs = []
    with open(pdf_path, "rb") as file:
        reader = pypdf.PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            page_paragraphs = text.split("\n\n")
            paragraphs.extend(page_paragraphs)
    return paragraphs

def split_into_sections(paragraphs, section_size):
    sections = []
    current_section = ""
    for i, paragraph in enumerate(paragraphs):
        cleaned_paragraph = clean_text(paragraph)
        current_section += cleaned_paragraph + " "
        if (i + 1) % section_size == 0:
            sections.append(current_section.strip())
            current_section = ""
    if current_section:
        sections.append(current_section.strip())
    return sections

def main(topic, pdf_file_path = "sample-pdf.pdf"):
    # Example usage
    paragraphs = parse_pdf_paragraphs(pdf_file_path)
    section_size = 3
    parsed_sections = split_into_sections(paragraphs, section_size)

    # Convert sections to DataFrame
    data = {
        "Section Number": range(len(parsed_sections)),
        "Content": parsed_sections
    }
    df = pd.DataFrame(data)
    df["Section Number"] = "section" + df["Section Number"].astype(str)
    df.to_csv("paper.csv", index=False)
    client = ff.Client(local=True)
    ff.register_user("featureformer").make_default_owner()

    local = ff.register_local()

    paper = local.register_file(
        name="paper",
        variant="fix_v4",
        description="A dataset of paper sections",
        path="paper.csv"
    )

    paper_df = client.dataframe(paper)
    paper_df.head()

    #feature transformation
    @local.df_transformation(inputs=[paper])
    def get_section_length(paper_df):
        """the average transaction amount for a user """
        paper_df["Section Length"] = paper_df["Content"].apply(lambda x: len(x))
        return paper_df
    
    full_df = client.dataframe(get_section_length)

    @local.df_transformation(inputs=[get_section_length])
    def vectorize_sections(full_df):
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(full_df["Content"].tolist())
        full_df["Vector"] = embeddings.tolist()
        
        return full_df
    
    PINECONE_API_KEY = '4628339c-b376-4efc-8190-fd52198e3e9b'
    PINECONE_ENVIRONMENT = 'us-west1-gcp-free'
    PINECONE_PROJECT_ID = 'e269605'

    pinecone = ff.register_pinecone(
        name="pinecone_v2",
        project_id = PINECONE_PROJECT_ID,
        environment = PINECONE_ENVIRONMENT,
        api_key = PINECONE_API_KEY
    )

    client.apply()

    @ff.entity
    class Section:
        section_embeddings = ff.Embedding(
            vectorize_sections[["Section Number", "Vector"]],
            dims=384,
            vector_db=pinecone,
            description="Embeddings created from sections of a paper",
            variant="v6"
        )
        sections = ff.Feature(
            get_section_length[["Section Number", "Content"]],
            type=ff.String,
            description="Sections and their original content",
            variant="v6"
        )

    @ff.ondemand_feature(variant="prototype_v6")
    def relevant_sections(client, params, entity):
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        search_vector = model.encode(params["query"])
        print(len(search_vector))
        res = client.nearest("section_embeddings", "v5", search_vector, k=1)
        return res
    
    query_topic = topic

    client.apply()
    client.features([("relevant_sections", "prototype_v6")], {}, params={"query": query_topic})
    @ff.ondemand_feature(variant="test2")
    def contextualized_prompt(client, params, entity):
        pks = client.features([("relevant_sections", "prototype_v6")], {}, params=params)
        prompt = "Use the following snippets from the paper to answer the following question\n"
        for pk in pks[0]:
            prompt += "```"
            prompt += client.features([("sections", "v5")], {"section": pk})[0]
            prompt += "```\n"
        prompt += "Question: "
        prompt += params["query"]
        prompt += "?"
        return prompt
    client.apply()
    client.features([("contextualized_prompt", "test2")], {}, params={"query": query_topic})

    Q, F = get_question("Business", "Impact of COVID on Small Businesses", 3)
    question_prompt = Q + F
    client.apply()
    q = question_prompt
    prompt = client.features([("contextualized_prompt", "test2")], {}, params={"query": q})[0]
    json_response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1000, # The max number of tokens to generate
        temperature=1.0 # A measure of randomness
    )["choices"][0]["text"]   
    return json_response