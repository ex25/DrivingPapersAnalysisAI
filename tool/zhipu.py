from zhipuai import ZhipuAI
from config import Zhipu_config
from tool.pdf import get_pdf_text

classification_prompt = """
任务：分析给定论文（标题和摘要）是否适用于智能驾驶领域，如适用则进行子领域分类（6个以内）。
角色：你是智能驾驶领域的专家，精通各个子领域的最新进展和技术应用。你能准确判断论文是否与智能驾驶相关，并能识别其主要贡献所属的具体子领域。
背景：智能驾驶是一个快速发展的跨学科领域，涉及计算机视觉、传感器融合、路径规划、决策控制等多个方面。近年来，深度学习和人工智能技术在该领域的应用日益广泛，带来了许多创新性的解决方案。
输出格式：
1. 应用判断：[Y/N]
2. 子领域分类：[子领域名称]（如应用判断为"Y"）
3. 分类理由：[简要说明论文与该子领域的关联及对智能驾驶的潜在贡献]

注意事项：
- 一定要保证格式完整，保留中括号！否则无法识别！！！
- 分析核心内容和创新点，选择最主要的子领域。
- 考虑技术或方法的应用潜力，保持客观严谨。
- 最多给出3行内容。
- 如输入与论文无关，按非智能驾驶相关提示回答，保持3行。
- 不用太直接关联，稍微有些关联也可以分类

子领域如下（限定以下领域，每一行都是一个完整的子领域（忽略后面括号的内容），请不要拆分，不要分类到其他领域！）：
道路场景理解与分析（包括车道线检测、交通标志识别、路况分析等）
车辆与行人检测跟踪（包括实时目标检测、多目标跟踪、姿态估计，图像增强等）
视觉导航与运动规划（包括视觉里程计、视觉SLAM、基于视觉的路径规划等）
定位、建图与路径规划
行为预测与决策控制
仿真与数据生成（包括虚拟环境构建、合成数据生成等）

请严格按照输出格式进行输出！（方括号内容可变，其他格式不变，包括保留方括号!!!）

"""

zero_shot_prompt = """
任务：分析给定的完整论文，提取其主要研究方法和核心思想。
角色：你是一位经验丰富的跨学科研究专家，精通各种科研方法论和最新技术趋势。你能够快速理解各个领域的学术论文，并准确提炼出其关键方法和核心思想。
背景：学术研究涉及广泛的领域和方法，包括但不限于实验研究、理论分析、计算机模拟、数据挖掘、机器学习等。每篇论文都有其独特的研究方法和核心思想，这些是理解和评估研究贡献的关键。
输出格式：
1. 研究方法：[简要描述论文采用的主要研究方法和技术]
2. 核心思想：[概括论文的主要创新点和核心贡献]

注意事项：
- 严格遵守输出格式，方括号不需要保留！
- 关注论文的创新性和独特贡献。
- 用简洁明了的语言概括，每项不超过5句话。
- 如果输入内容不是学术论文，请说明无法分析并简要解释原因。
- 保持客观中立的分析态度。

请仔细阅读整篇论文，包括但不限于标题、摘要、引言、方法、结果和讨论部分，然后按照上述格式输出分析结果。确保你的分析全面且准确地反映了论文的核心内容。

"""

few_shot_prompt = """
任务：分析给定的完整论文，提取其主要研究方法和核心思想。
角色：你是一位经验丰富的跨学科研究专家，精通各种科研方法论和最新技术趋势。你能够快速理解各个领域的学术论文，并准确提炼出其关键方法和核心思想。
背景：学术研究涉及广泛的领域和方法，包括但不限于实验研究、理论分析、计算机模拟、数据挖掘、机器学习等。每篇论文都有其独特的研究方法和核心思想，这些是理解和评估研究贡献的关键。
输出格式：
1. 研究方法：[简要描述论文采用的主要研究方法和技术]
2. 核心思想：[概括论文的主要创新点和核心贡献]

注意事项：
- 严格遵守输出格式，保留方括号！
- 关注论文的创新性和独特贡献。
- 用简洁明了的语言概括，每项不超过3句话。
- 如果输入内容不是学术论文，请说明无法分析并简要解释原因。
- 保持客观中立的分析态度。

示例1：
论文：[论文1的完整内容，包括标题、摘要、引言、方法、结果、讨论等]
分析：
1. 研究方法：该研究采用了深度学习方法，使用改进的卷积神经网络结构处理图像分类任务。研究者提出了新的注意力机制，以更好地捕捉图像中的关键特征。
2. 核心思想：通过引入注意力机制来提高卷积神经网络的性能，使模型能够更好地关注图像中的重要区域，从而提高分类准确率。该方法在处理复杂场景和细粒度分类任务时表现尤为出色。

示例2：
论文：[论文2的完整内容]
分析：
1. 研究方法：该研究提出了一种新的自然语言处理模型，结合了Transformer架构和强化学习技术。研究者设计了特殊的奖励函数，用于指导模型生成更加连贯和信息丰富的文本。
2. 核心思想：将强化学习引入到文本生成任务中，通过优化长期奖励来提高生成文本的质量。这种方法能够克服传统序列到序列模型中的exposure bias问题，生成更加自然和连贯的长文本。

示例3：
论文：[论文3的完整内容]
分析：
1. 研究方法：该研究提出了一种新的联邦学习算法，能够在保护数据隐私的同时提高模型性能。研究者设计了安全聚合协议，使参与方可以安全地共享模型更新而不泄露原始数据。
2. 核心思想：通过改进联邦学习中的通信效率和隐私保护机制，使分布式机器学习在实际应用中更加可行。该方法特别适用于涉及敏感数据的场景，如医疗健康领域。

"""


def get_classification_result_by_zhipu(content):
    if content is None or content == "":
        return []
    client = ZhipuAI(api_key=Zhipu_config.API_KEY)
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": classification_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
    )
    print(response)
    result = response.choices[0].message.content.split("\n")
    return result


def get_classification_response_by_zhipu_async(content):
    if content is None or content == "":
        return []
    client = ZhipuAI(api_key=Zhipu_config.API_KEY)
    response = client.chat.asyncCompletions.create(
        model="glm-4-0520",  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": classification_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
    )
    return response


def check_zhipu_async_classification_result(response):
    if response is None:
        return []
    client = ZhipuAI(api_key=Zhipu_config.API_KEY)

    task_id = response.id
    result_response = client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
    task_status = result_response.task_status

    if task_status == 'SUCCESS':
        result = result_response.choices[0].message.content.split("\n")
        return result
    elif task_status == 'FAILED':
        return None
    else:
        return []


def get_zero_shot_result_by_zhipu(content):
    if content is None or content == "":
        return []
    client = ZhipuAI(api_key=Zhipu_config.API_KEY)
    response = client.chat.completions.create(
        model="glm-4-0520",  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": zero_shot_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
    )
    result = response.choices[0].message.content.split("\n")
    return result


def get_few_shot_result_by_zhipu(content):
    if content is None or content == "":
        return []
    client = ZhipuAI(api_key=Zhipu_config.API_KEY)
    response = client.chat.completions.create(
        model="glm-4-0520",  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": few_shot_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.2,
    )
    result = response.choices[0].message.content.split("\n")
    return result


if __name__ == '__main__':
    text = get_pdf_text("../data/pdfs"
                        "/Song_Collaborative_Semantic_Occupancy_Prediction_with_Hybrid_Feature_Fusion_in_Connected_CVPR_2024_paper.pdf")
    print(get_zero_shot_result_by_zhipu(text))
    print(get_few_shot_result_by_zhipu(text))
