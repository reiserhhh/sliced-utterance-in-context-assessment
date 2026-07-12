# SUICA-Native Corpus — Prompt Battery v1 (bilingual; frozen on seal)

Companion to PROTOCOL_V1.md. Arm A keeps the CHOICE channel alive (participants pick
their rinds); Arm B closes it by design (identical prompts for everyone), licensing
condition adjustment per F4's boundary condition. JP versions are translations of
intent, not literal strings; both versions freeze together at prereg.

## A. Arm A — free regime (choice channel ALIVE)

Instruction (EN): "Below are loose starting points. Pick any 3 of the 5 — whichever
you actually feel like writing about — and write freely. There are no right answers and
no required structure; write as you would anywhere you normally write."
Instruction (JP): 「以下はゆるい出発点です。5つのうち、実際に書きたいと思う3つを選び、
自由に書いてください。正解も決まった構成もありません。普段どこかに書くときのままで。」

1. Something on your mind lately / 最近ずっと頭にあること
2. A place, game, hobby, or community you keep going back to / つい戻ってしまう場所・
   ゲーム・趣味・コミュニティ
3. Something that annoyed you or made you laugh this week / 今週いらっとした、あるいは
   笑ったこと
4. A plan, project, or decision you are working through / いま進めている計画・プロジェクト・
   迷っている決断
5. Anything else — your topic, your rules / その他 — 話題も流儀もあなた次第

(Design note: topic CHOICE among 1-5 is itself recorded as the choice observation; the
"anything else" slot preserves full rind freedom.)

## B. Arm B — fixed regime (choice channel CLOSED)

### B1. Fixed writing prompts (all participants, same order)

1. EN: "Describe, in as much detail as you can, how your last week actually went —
   what you did, where, with whom." / JP: 「先週が実際にどう過ぎたかを、できるだけ
   詳しく書いてください — 何を、どこで、誰として。」
2. EN: "Explain something you know well to someone who knows nothing about it." /
   JP: 「あなたがよく知っていることを、まったく知らない人に説明してください。」
3. EN: "Describe a disagreement you had (recent or old) — what happened, what each
   side wanted." / JP: 「あなたが経験した意見の対立(最近でも昔でも)について — 何が
   起き、それぞれが何を望んでいたか。」

### B2. Dialogue block — FROZEN interviewer script (no adaptive probing)

System prompt for the AI interviewer (published verbatim; deploy as-is):

    You are a fixed-script interviewer for a research study. Ask EXACTLY the
    questions below, one at a time, in order. After each participant answer, your
    entire next turn is the next question, optionally preceded by at most one short
    neutral acknowledgement of five words or fewer (e.g., "Thank you." / "I see.").
    Never rephrase the participant's words, never summarize their answer, never offer
    interpretations, advice, or follow-up probes, never use evaluative or clinical
    vocabulary. If the participant asks you a question, reply only: "I can't discuss
    that during the interview — please answer in whatever way feels natural."
    Questions:
    Q1 How do your weekdays and weekends differ, if at all?
    Q2 What do you usually do when a plan you cared about falls through?
    Q3 Tell me about the last time you changed your mind about something.
    Q4 What kinds of situations do you tend to avoid, and how do you manage that?
    Q5 What would the people closest to you say is most typical of you?
    Q6 Is there anything you have been putting off? What makes it easy to put off?

    (JP deployment: same rules; questions translated at freeze:
    Q1 平日と週末はどう違いますか(違うとすれば)。 Q2 大事にしていた予定が流れたとき、
    普段どうしますか。 Q3 最近、何かについて考えを変えたときのことを教えてください。
    Q4 どんな状況を避けがちですか。どうやってやり過ごしていますか。 Q5 一番身近な人
    たちは、あなたの「らしさ」を何と言うと思いますか。 Q6 先延ばしにしていることは
    ありますか。なぜ先延ばしにしやすいのでしょう。)

Echo-minimizing constraints are structural (five-word acknowledgements, no rephrasing),
so assistant-echo should be near floor; the monitor (PROTOCOL section 5) verifies rather
than assumes.

## C. Freeze note

At prereg seal: this file's SHA-256 is recorded in the seal commit; any post-seal edit
voids the confirmatory status of affected blocks.
