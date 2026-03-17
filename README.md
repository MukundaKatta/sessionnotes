# SessionNotes

AI Therapy Note Generator - automatically generate structured clinical notes from therapy session transcripts.

## Features

- **SOAP Notes** - Subjective, Objective, Assessment, Plan format
- **DAP Notes** - Data, Assessment, Plan format
- **BIRP Notes** - Behavior, Intervention, Response, Plan format
- **Theme Extraction** - Identify recurring themes and topics from sessions
- **Progress Tracking** - Compare client progress across multiple sessions
- **Risk Screening** - Flag safety concerns (suicidal ideation, self-harm, substance abuse)
- **Rich Reports** - Beautiful terminal output with Rich

## Installation

```bash
pip install -e .
```

## Usage

### Generate a SOAP Note

```bash
sessionnotes generate --format soap --transcript "Client reported feeling anxious..."
```

### Generate a DAP Note

```bash
sessionnotes generate --format dap --transcript "Client discussed relationship conflicts..."
```

### Generate a BIRP Note

```bash
sessionnotes generate --format birp --transcript "Client arrived on time, appeared well-groomed..."
```

### Analyze Themes

```bash
sessionnotes analyze themes --transcript "Client discussed work stress and family conflicts..."
```

### Screen for Risk

```bash
sessionnotes analyze risk --transcript "Client mentioned feeling hopeless..."
```

### Generate Report

```bash
sessionnotes report --client-id CLIENT001 --sessions session1.json session2.json
```

## Note Formats

### SOAP (Subjective, Objective, Assessment, Plan)
- **Subjective**: Client's self-reported experiences, feelings, and concerns
- **Objective**: Therapist's observations of client behavior, affect, and presentation
- **Assessment**: Clinical interpretation, diagnosis considerations, and progress evaluation
- **Plan**: Treatment goals, interventions, and next steps

### DAP (Data, Assessment, Plan)
- **Data**: All relevant information gathered during the session
- **Assessment**: Clinical interpretation and analysis
- **Plan**: Future treatment directions and action items

### BIRP (Behavior, Intervention, Response, Plan)
- **Behavior**: Observable client behaviors and presenting issues
- **Intervention**: Therapeutic techniques and interventions used
- **Response**: Client's response to interventions
- **Plan**: Next steps and future session planning

## License

MIT
