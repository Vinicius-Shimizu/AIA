import ReactMarkdown from "react-markdown";

const MessageBox = (props) => {
    const {content, sender} = props;
    
    const isUser = sender === "user";
    const boxClass = isUser 
                ? "bg-gray-700 max-w-[500px] border-gray-600" 
                : "bg-zinc-700 border-zinc-600";
    const align = isUser 
                ? "justify-end"
                : "justify-start"
    return (
        <div className={`flex ${align}`}>
            <div 
                className={`border-2  p-4 m-4 rounded-lg w-fit h-fit ${boxClass} text-left text-justify`}
            >
                <ReactMarkdown>{content}</ReactMarkdown>
            </div>

        </div>
    )
};

export default MessageBox;