#
# 用法: uv run python pdf_agent.py --pdf_path "D:\\path\\to\\your\\doc.pdf"
#
import asyncio
import argparse
import os
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

app = MCPApp(
    name="pdf_summary_agent_from_config"
)

# --- 2. 你的 main 函数 ---
async def main(pdf_path: str):
    """
    运行一个自主的 Agent，它会使用 mcp_agent.config.yaml 中定义的所有配置。
    """
    
    # app.run() 会自动启动 YAML 中定义的所有服务器
    async with app.run() as mcp_agent_app:
        logger = mcp_agent_app.logger
        
        pdf_agent = Agent(
            name="pdf_researcher",
            instruction="""You are a helpful research assistant.
            You can read local files using 'filesystem' and read PDF content using 'pdf-reader'.
            Use the 'pdf-reader' tools (like read_pdf_with_ocr) when asked to analyze a PDF.
            Use 'filesystem' tools (like list_files) for general file operations.""",
            
            # 它会从 YAML 加载的配置中找到这两个服务器
            server_names=["filesystem", "pdf-reader"],
        )

        # 启动 Agent (它会自动连接到 YAML 中定义的服务器)
        async with pdf_agent:
            tools = await pdf_agent.list_tools()
            # logger.info("Agent 'pdf_researcher' 已连接。可用工具:", data=tools)

            # --- 3. 【核心】附加 LLM ---
            #
            # `attach_llm()` 会自动使用 YAML 中定义的 'openai' 配置
            # (即 Aliyun 的 base_url 和 qwen-turbo 模型)
            #
            llm = await pdf_agent.attach_llm(OpenAIAugmentedLLM)

            # logger.info(f"LLM 已附加 (Provider: {llm.provider_name}, Model: {llm.model_name})")

            # --- 4. 运行你的任务 ---

            # 任务 1: 【核心】运行 PDF 总结任务
            # result_pdf = await llm.generate_str(
            #     message=f"请提取pdf里面所有的图片: {pdf_path}"
            # )
            # logger.info(f"PDF Summary Result: {result_pdf}")
            # --- 4. 运行你的任务 ---

            # 【新任务2】：定义图片保存的路径
            output_image_dir = "D:\agent\my_images" # (r"..." 是为了防止 \ 被转义)

            # 【新指令】：给 LLM 一个明确的提取图片指令
            new_message = (
                f"Please extract all images from the PDF at '{pdf_path}' "
                f"and save them to the directory '{output_image_dir}'."
            )
            
            logger.info(f"向 Agent 提交新任务: {new_message}")

            # 任务 2: 【核心】运行 PDF 提取图片任务
            result_extraction = await llm.generate_str(
            message=new_message
            )
            
            # LLM 会返回一个确认信息
            logger.info(f"Image Extraction Result: {result_extraction}")  
            

# --- 3. 你的 argparse (保持不变) ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Summarize a PDF using an autonomous agent.')
    parser.add_argument(
        '--pdf_path', 
        type=str, 
        required=True, 
        help='The absolute path to the PDF file to summarize'
    )
    args = parser.parse_args()
    
    # 检查 API Key 是否已设置
    if not os.environ.get("OPENAI_API_KEY"):
         print("="*50)
         print("错误: 请先设置 `OPENAI_API_KEY` 环境变量！")
         print("（mcp-agent 会读取它并用于 'openai:' 配置）")
         print("="*50)
    else:
        print(f"Starting PDF Agent to summarize: {args.pdf_path}")
        print("将自动加载 mcp_agent.config.yaml 中的配置...")
        asyncio.run(main(args.pdf_path))