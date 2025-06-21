
"use client";

import { ThumbsUp, ThumbsDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

interface FeedbackButtonsProps {
  className?: string;
  onFeedback?: (feedback: "good" | "bad") => void;
}

export function FeedbackButtons({ className, onFeedback }: FeedbackButtonsProps) {
  const { toast } = useToast();

  const handleFeedback = (feedback: "good" | "bad") => {
    if (onFeedback) {
      onFeedback(feedback);
    }
    toast({
      title: "Feedback Received",
      description: `Thank you for your ${feedback === "good" ? "positive" : "negative"} feedback!`,
    });
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleFeedback("good")}
        aria-label="Good response"
      >
        <ThumbsUp className="mr-2 h-4 w-4" /> Good
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleFeedback("bad")}
        aria-label="Bad response"
      >
        <ThumbsDown className="mr-2 h-4 w-4" /> Bad
      </Button>
    </div>
  );
}
