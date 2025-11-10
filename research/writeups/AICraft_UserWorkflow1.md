# Previous Experiments

Below are the experiments that I have previously done that informed the core user workflow that I want to currently instantiate.

<experiments>
I want you to prototype the following with the methodology of Comparatively Structured Observations. That is, the prototype should tease out the important design aspects without being overly complete so that I understand the full context of what is going on. Each of this prototype should be in a different git worktree, and you should open these prototypes for me in the browser to browse after they are finished. For each of the prototypes, generate 3 different versions. 

First, I want you to give the agent that the child is customizing more of a personality. We should let the backend generate a backstory to the agent given the system prompt that the child is entering. Further, we also want to generate an avatar for the agent. The avatar shoudl be generated through Flux using the mflux-generate cli. Note that here is the actual command that you could use: 
```bash
mflux-generate --model schnell --path ./models/schnell-3bit --prompt "your prompt here" --steps 2
```

Second, I want the experience to be much more interactive. I want a child to be able to deploy the agent in different scenarios really easily and see how they perform. These can be simple "RL environments". Note that there are complexities in that after generating these environments (games, mazes, etc..), you should guide the child towards teaching the agent to the kind of tools that the agent should have access to in the environment (like moving up, moving down, etc..). Think about the turtle microworld in LOGO.

Third, I want you to be inspired by MindCraft. There are multi-agent collaboration benchmarks in MindCraft. Goto /Users/wz/Desktop/zPersonalProjects/AICraft/research/mindcraft to see my thoughts there. This is the exact prompt: /Users/wz/Desktop/zPersonalProjects/AICraft/research/mindcraft/prompt.xml.
</experiments>

# Core Children Workflow

See @AICraft.md for the whole context.

1. First, the user goes in and can generate an Avatar and Backstory for their agent. Except for the avatar and the backstory, the agent currently doesn't have any other functions.
2. Then, the user can start generating a virtual world/game for the agent to play in.
   1. Q1: How to generate this virtual world?
   2. Q2: Each virtual world should have well-defined operations!
3. Initially, the agent does not have any tools to operate in the virtual world.
   1. Then, the user is able to add tools that it has access to. Starting off with the most basic tools (moving forward, backward, etc..)
   2. And then the user is able to add more advanced tools that specify more complicated high level behaviors to make the agent better at the game
   3. The user can also inject more knowledge into the agent when they see that the agent is not acting in an optimal manner by adding to the agent's memory
   4. The user can also teach the agent how to remember things. We should come with memory building blocks that the user can use.
   5. (Look at the )
4. After the user is satisfied with the agent in this one virtual world, the user can move the agent into the next virtual world, or to progress to add more intricate game mechanics to the current world.
5. At last, the user should be able to export the agent to run on their own computer.

Note that everything the user does, they do not have to look at the code, but can input in natural langauge commands, where an agent will take it and turn it to code if there needs to be code modifications. 

I want you to based on this give me an active plan on 