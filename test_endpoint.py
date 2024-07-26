import requests
import time  # Step 1: Import the time module

def split_string_to_lines(input_string, max_length=200):
    words = input_string.split()
    lines = []
    current_line = []

    for word in words:
        # Check if adding the next word would exceed the max length
        if len(' '.join(current_line + [word])) <= max_length:
            current_line.append(word)
        else:
            # If it exceeds, add the current line to lines and start a new line
            lines.append(' '.join(current_line))
            current_line = [word]

    # Add the last line if there are remaining words
    if current_line:
        lines.append(' '.join(current_line))

    return lines

# Define the URL of the Flask app's `/generate` endpoint
url = "http://192.168.0.243:5000/generate"
string = """Certainly! Here's a long text that discusses the history and impact of the printing press:

---

The invention of the printing press is often regarded as one of the most significant milestones in human history. It marked the beginning of a revolution in communication, education, and knowledge dissemination that transformed societies and cultures around the world.

The origins of the printing press can be traced back to China, where woodblock printing was developed during the Tang Dynasty (618-907 AD). This technique involved carving characters and images onto wooden blocks, inking the blocks, and pressing them onto paper. Woodblock printing allowed for the production of books and documents, but it was labor-intensive and not suitable for large-scale production.

A major breakthrough came in the mid-15th century with Johannes Gutenberg's invention of the movable type printing press in Mainz, Germany. Gutenberg's press used individual metal letters that could be rearranged to form words and sentences. This innovation made it possible to print multiple copies of a text quickly and efficiently, significantly reducing the cost and time required to produce books.

Gutenberg's most famous work, the Gutenberg Bible, was printed around 1455. It was the first major book produced using movable type and marked the beginning of the "Gutenberg Revolution." The press's impact was profound, leading to an explosion of printed materials and a dramatic increase in literacy rates. Books, pamphlets, and other printed materials became more accessible to a broader audience, breaking the monopoly that religious and academic institutions had on knowledge.

The spread of the printing press across Europe had far-reaching consequences. It played a crucial role in the Renaissance by facilitating the dissemination of classical texts and new ideas. Scholars and thinkers such as Erasmus, Martin Luther, and Galileo Galilei used the press to share their works, challenging established doctrines and promoting scientific inquiry and humanism.

The Reformation, a religious movement in the 16th century, was significantly influenced by the printing press. Martin Luther's Ninety-Five Theses, which criticized the Catholic Church's practices, were widely distributed thanks to the press. This enabled the rapid spread of Protestant ideas and contributed to the fragmentation of the Catholic Church and the rise of various Protestant denominations.

In addition to its impact on religion and education, the printing press also transformed the world of business and communication. The ability to produce printed documents efficiently led to the rise of newspapers and periodicals, which became essential tools for spreading news and information. The first newspaper, "Relation," was published in Strasbourg in 1605, and newspapers quickly became a staple of daily life, informing the public about current events and shaping public opinion.

The printing press also played a pivotal role in the development of modern science. The ability to print and distribute scientific works allowed researchers to share their findings with a wider audience, facilitating collaboration and the advancement of knowledge. The publication of Isaac Newton's "Philosophic Naturalis Principia Mathematica" in 1687, for example, laid the foundations for classical mechanics and had a lasting impact on the scientific community.

As the technology of the printing press evolved, so did its impact. The Industrial Revolution of the 18th and 19th centuries brought further advancements in printing technology, such as the steam-powered press and later the rotary press, which increased the speed and volume of printing. These innovations made printed materials even more accessible and affordable, contributing to the spread of education and literacy.

In the 20th century, the printing press continued to evolve with the advent of digital printing and the rise of the internet. Digital printing technology allowed for on-demand printing, reducing waste and enabling the production of customized materials. The internet, meanwhile, revolutionized the way information is disseminated, with digital publications and online platforms becoming the primary means of communication and information sharing.

Despite the rise of digital media, the printing press remains a vital tool for producing books, newspapers, and other printed materials. Its legacy is evident in the continued importance of print in education, literature, and journalism. The printed word still holds a special place in our culture, providing a tangible connection to knowledge and ideas that digital media cannot fully replicate.

In conclusion, the invention of the printing press by Johannes Gutenberg was a transformative event in human history. It revolutionized the way information was produced and shared, leading to significant advancements in education, science, religion, and communication. The printing press laid the groundwork for the modern world, shaping societies and cultures in ways that continue to resonate today. Its impact is a testament to the power of technology to drive progress and change, highlighting the enduring importance of innovation in shaping our collective future."""
# Define "Lorem Ipsum" lines, one for each style
lines = split_string_to_lines(string)

# Define biases and styles for each line
biases = [0.5 for i in range(1, len(lines) + 1)]
styles = [5 for i in range(1, len(lines) + 1)]

# Ensure stroke_colors and stroke_widths lists match the number of lines
stroke_colors = ["black"] * len(lines)
stroke_widths = [1] * len(lines)

# Create a sample payload with the lines, biases, and styles
payload = {
    "lines": lines,
    "biases": biases,
    "styles": styles,
    "stroke_colors": stroke_colors,
    "stroke_widths": stroke_widths
}

# Record the current time before sending the request
start_time = time.time()  # Step 2

# Send a POST request to the endpoint with the JSON payload
response = requests.post(url, json=payload)

# Record the time immediately after the request is completed
end_time = time.time()  # Step 3

# Calculate the response time
response_time = end_time - start_time  # Step 4

# Print the response time
print(f"Response time: {response_time} seconds")  # Step 5

# Print the response from the server
path_data = response.json().get('path', '')

# Specify the filename where you want to save the data
filename = 'output_path.svg'

# Open the file in write mode and write the path_data to it
with open(filename, 'w') as file:
    file.write(path_data)

print(f"Path data saved to {filename}")