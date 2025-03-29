## CaP-Options

Builds on the Cliport repo and accompanying Ravens benchmark, we removed a lot of code, but there's still a lot of unused code left from it, mostly in the environments folder and in utils.

The core type for Point3D was probably a mistake, might make sense to refactor that (just make it an alias for np.array?).

Interaction is structured as follows:

- parse skill to learn
  - set up a task
    - attempt to solve task with corrections

See agents.model for data classes, Skill, TaskExample, InteractionTrace and EnvironmentConfig - used for storing and retrieving and basic convenience functions
